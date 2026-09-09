"""Bounded GET-only GitHub transport. Credentials never enter saved metadata."""
from __future__ import annotations

import http.client
import os
import re
import socket
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

from .store import CorpusError, require

SAFE_HEADERS = {'etag', 'last-modified', 'link', 'retry-after', 'x-ratelimit-limit',
                'x-ratelimit-remaining', 'x-ratelimit-reset', 'x-ratelimit-resource',
                'x-github-request-id', 'x-github-api-version-selected', 'content-type',
                'content-length', 'location', 'date'}


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    require(p.scheme == 'https' and p.netloc == 'api.github.com' and not p.fragment,
            'GitHub API HTTPS host required')
    require(p.path in ('/versions', '/search/issues') or re.fullmatch(
        r'/(?:repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|repositories/\d+)(?:/(?:issues|pulls)/\d+(?:/(?:comments|timeline|reviews|files))?)?', p.path),
            'Endpoint outside collector allowlist')
    return url


def token_from_environment():
    for name in ('GH_TOKEN', 'GITHUB_TOKEN'):
        if os.environ.get(name):
            return os.environ[name]
    try:
        result = subprocess.run(['gh', 'auth', 'token', '--hostname', 'github.com'],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    raise CorpusError('GitHub authentication unavailable; set GH_TOKEN or run gh auth login')


@dataclass
class Response:
    status: int = 0
    headers: dict = field(default_factory=dict)
    body: bytes = b''
    error: str | None = None
    origin: str = 'real'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHubHTTP:
    def __init__(self, token=None):
        self.token = token if token is not None else token_from_environment()
        self.opener = urllib.request.build_opener(NoRedirect)

    def get(self, url, *, api_version, etag=None, max_bytes, timeout):
        safe_url(url)
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'brrr-corpus/1',
                   'X-GitHub-Api-Version': api_version, 'Authorization': f'Bearer {self.token}',
                   'Accept-Encoding': 'identity'}
        if etag:
            headers['If-None-Match'] = etag
        req = urllib.request.Request(url, headers=headers, method='GET')
        try:
            try:
                response = self.opener.open(req, timeout=timeout)
            except urllib.error.HTTPError as e:
                response = e
            with response:
                saved = {k.lower(): v for k, v in response.headers.items() if k.lower() in SAFE_HEADERS}
                body = response.read(max_bytes + 1)
                if len(body) > max_bytes:
                    return Response(response.code, saved, body[:max_bytes], 'RESPONSE_TOO_LARGE')
                length = saved.get('content-length')
                if length and response.code != 304 and int(length) != len(body):
                    return Response(response.code, saved, body, 'TRUNCATED_BODY')
                return Response(response.code, saved, body)
        except (socket.timeout, TimeoutError):
            return Response(error='TIMEOUT')
        except http.client.IncompleteRead as e:
            return Response(body=e.partial[:max_bytes], error='TRUNCATED_BODY')
        except (urllib.error.URLError, OSError, http.client.HTTPException, ValueError):
            return Response(error='TRANSPORT_ERROR')  # Do not echo exception text containing headers.
