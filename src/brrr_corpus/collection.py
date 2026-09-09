"""Durable GitHub collection, page checkpoints, leases and explicit partial coverage."""
from __future__ import annotations

import json
import re
import time
import uuid
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from .collection_plan import implementation_hash, search_url
from .github_http import SAFE_HEADERS, GitHubHTTP, safe_url
from .store import CorpusError, canonical, digest, require

TERMINAL = ('SUCCEEDED', 'PARTIAL', 'FAILED_FINAL', 'BLOCKED', 'SPLIT')


def setup(c):
    c.db.executescript('''
        CREATE TABLE IF NOT EXISTS collections (
            id TEXT PRIMARY KEY, plan_id TEXT REFERENCES records(id), epoch TEXT NOT NULL,
            parent_id TEXT, created_at REAL NOT NULL, requests INTEGER NOT NULL DEFAULT 0,
            bytes INTEGER NOT NULL DEFAULT 0, not_before REAL NOT NULL DEFAULT 0,
            next_core REAL NOT NULL DEFAULT 0, next_search REAL NOT NULL DEFAULT 0,
            stop_reason TEXT, UNIQUE(plan_id, epoch));
        CREATE TABLE IF NOT EXISTS collection_jobs (
            id TEXT PRIMARY KEY, collection_id TEXT REFERENCES collections(id),
            url TEXT NOT NULL, role TEXT NOT NULL, spec TEXT NOT NULL, repository TEXT NOT NULL,
            root TEXT NOT NULL, priority INTEGER NOT NULL, state TEXT NOT NULL DEFAULT 'PENDING',
            token INTEGER NOT NULL DEFAULT 0, lease_until REAL NOT NULL DEFAULT 0,
            attempts INTEGER NOT NULL DEFAULT 0, retry_at REAL NOT NULL DEFAULT 0,
            error TEXT, result_id TEXT REFERENCES records(id));
        CREATE INDEX IF NOT EXISTS collection_jobs_queue ON collection_jobs(collection_id,state,priority);
        CREATE TABLE IF NOT EXISTS collection_repos (
            collection_id TEXT REFERENCES collections(id), repository TEXT NOT NULL,
            state TEXT NOT NULL, PRIMARY KEY(collection_id, repository));
        CREATE TABLE IF NOT EXISTS collection_repository_ids (
            collection_id TEXT REFERENCES collections(id), repository TEXT NOT NULL,
            provider_id INTEGER NOT NULL, canonical_name TEXT NOT NULL,
            PRIMARY KEY(collection_id, repository));
        CREATE TABLE IF NOT EXISTS collection_targets (
            collection_id TEXT REFERENCES collections(id), root TEXT NOT NULL,
            repository TEXT NOT NULL, number INTEGER NOT NULL, depth INTEGER NOT NULL,
            PRIMARY KEY(collection_id, root));
        CREATE TABLE IF NOT EXISTS collection_lane_members (
            collection_id TEXT REFERENCES collections(id), lane TEXT NOT NULL, root TEXT NOT NULL,
            PRIMARY KEY(collection_id, lane, root));
        CREATE TABLE IF NOT EXISTS collection_cache (
            cache_key TEXT PRIMARY KEY, body_blob TEXT REFERENCES objects(hash), headers TEXT NOT NULL);
    ''')


def queue(c, cid, url, role, spec=None, repository='', root='', priority=10):
    safe_url(url)
    spec = spec or {}
    jid = digest(canonical([cid, url, role, spec, repository, root]))
    c.db.execute('INSERT OR IGNORE INTO collection_jobs(id,collection_id,url,role,spec,repository,root,priority) VALUES(?,?,?,?,?,?,?,?)',
                 (jid, cid, url, role, canonical(spec).decode(), repository, root, priority))
    return jid


def add_repository(c, cid, repo):
    row = c.db.execute('INSERT OR IGNORE INTO collection_repos VALUES(?,?,?)', (cid, repo, 'PENDING'))
    if row.rowcount:
        queue(c, cid, f'https://api.github.com/repos/{repo}', 'repository', repository=repo, priority=0)


def add_target(c, cid, recipe, repo, number, depth=0, lane=None):
    require(isinstance(repo, str) and re.fullmatch(r'[\w.-]+/[\w.-]+', repo), 'INVALID_REPOSITORY')
    require(type(number) is int and number > 0, 'INVALID_ISSUE_NUMBER')
    root = f'{repo.lower()}#{number}'
    existing = c.db.execute('SELECT 1 FROM collection_targets WHERE collection_id=? AND root=?', (cid, root)).fetchone()
    if lane:
        member = c.db.execute('SELECT 1 FROM collection_lane_members WHERE collection_id=? AND lane=? AND root=?', (cid, lane, root)).fetchone()
        if member:
            return True
        count = c.db.execute('SELECT count(*) FROM collection_lane_members WHERE collection_id=? AND lane=?', (cid, lane)).fetchone()[0]
        limit = next(x['max_resources'] for x in recipe['lanes'] if x['id'] == lane)
        if count >= limit:
            return False
    if not existing:
        count = c.db.execute('SELECT count(*) FROM collection_targets WHERE collection_id=?', (cid,)).fetchone()[0]
        if count >= recipe['limits']['resources']:
            return False
        add_repository(c, cid, repo)
        c.db.execute('INSERT INTO collection_targets VALUES(?,?,?,?,?)', (cid, root, repo, number, depth))
        queue(c, cid, f'https://api.github.com/repos/{repo}/issues/{number}', 'issue',
              {'number': number, 'depth': depth}, repo, root)
    if lane:
        c.db.execute('INSERT OR IGNORE INTO collection_lane_members VALUES(?,?,?)', (cid, lane, root))
    return True


def start_collection(c, plan_id, *, refresh_of=None, now=None):
    setup(c)
    plan = c.get(plan_id, 'collection_plan')
    require(plan['implementation_hash'] == implementation_hash(), 'Collector changed; create a new plan')
    epoch = str(uuid.uuid4()) if refresh_of else 'initial'
    cid = digest(canonical([plan_id, epoch]))
    with c.transaction():
        inserted = c.db.execute('INSERT OR IGNORE INTO collections(id,plan_id,epoch,parent_id,created_at) VALUES(?,?,?,?,?)',
                                (cid, plan_id, epoch, refresh_of, now if now is not None else time.time())).rowcount
        if not inserted:
            return cid
        queue(c, cid, 'https://api.github.com/versions', 'versions', priority=-1)
        for repo in plan['repositories']:
            add_repository(c, cid, repo)
        for seed in plan['seeds']:
            add_target(c, cid, plan['recipe'], seed['repository'], seed['number'])
        if refresh_of:
            for row in c.db.execute('SELECT * FROM collection_targets WHERE collection_id=?', (refresh_of,)).fetchall():
                require(add_target(c, cid, plan['recipe'], row['repository'], row['number'], row['depth']),
                        'Refresh would omit known resources; use a recipe with adequate resource budget')
        for spec in plan['queries']:
            queue(c, cid, search_url(spec), 'search', spec, spec['repository'], priority=20)
    return cid


def resolve_collection(c, value):
    setup(c)
    if value == 'latest':
        row = c.db.execute('SELECT id FROM collections ORDER BY created_at DESC,rowid DESC LIMIT 1').fetchone()
    else:
        row = c.db.execute('SELECT id FROM collections WHERE id=?', (value,)).fetchone()
    require(row is not None, 'Collection not found')
    return row[0]


def lease_job(c, cid, recipe, now):
    with c.transaction():
        collection = c.db.execute('SELECT * FROM collections WHERE id=?', (cid,)).fetchone()
        if collection['not_before'] > now:
            return None, 'RATE_WAIT'
        versions = c.db.execute("SELECT state FROM collection_jobs WHERE collection_id=? AND role='versions'", (cid,)).fetchone()
        rows = c.db.execute('''SELECT * FROM collection_jobs WHERE collection_id=? AND
            (state='PENDING' OR (state='RETRY_WAIT' AND retry_at<=?) OR
             (state='RUNNING' AND lease_until<=?)) ORDER BY priority,rowid''', (cid, now, now)).fetchall()
        for row in rows:
            if row['role'] != 'versions' and versions[0] != 'SUCCEEDED':
                continue
            if row['role'] not in ('repository', 'versions') and row['repository']:
                repo = c.db.execute('SELECT state FROM collection_repos WHERE collection_id=? AND repository=?',
                                    (cid, row['repository'])).fetchone()
                if repo is None or repo[0] != 'PUBLIC':
                    continue
            rate = collection['next_search'] if row['role'] == 'search' else collection['next_core']
            if rate > now:
                continue
            if collection['requests'] >= recipe['limits']['total_requests'] or collection['bytes'] + recipe['limits']['response_bytes'] > recipe['limits']['total_bytes']:
                return None, 'TOTAL_BUDGET_EXHAUSTED'
            token = row['token'] + 1
            c.db.execute("UPDATE collection_jobs SET state='RUNNING',token=?,lease_until=?,attempts=attempts+1,error=NULL WHERE id=?",
                         (token, now + recipe['http']['lease_seconds'], row['id']))
            # Reserve the whole response allowance; a crashed attempt remains charged conservatively.
            c.db.execute('UPDATE collections SET requests=requests+1,bytes=bytes+?,next_core=?,next_search=? WHERE id=?',
                         (recipe['limits']['response_bytes'], now + recipe['http']['min_interval_seconds'],
                          now + recipe['http']['search_interval_seconds'] if row['role'] == 'search' else collection['next_search'], cid))
            return dict(c.db.execute('SELECT * FROM collection_jobs WHERE id=?', (row['id'],)).fetchone()), None
    return None, 'NO_RUNNABLE_JOB'


def check_lease(c, job, now):
    row = c.db.execute('SELECT state,token,lease_until FROM collection_jobs WHERE id=?', (job['id'],)).fetchone()
    require(row and row['state'] == 'RUNNING' and row['token'] == job['token'] and row['lease_until'] > now,
            'STALE_FENCING_TOKEN_OR_EXPIRED_LEASE')


def next_link(headers, current, *, identity=None):
    links = re.findall(r'<([^>]+)>\s*;\s*rel="([^"]+)"', headers.get('link', ''))
    result = [safe_url(urljoin(current, url)) for url, rel in links if 'next' in rel.split()]
    require(len(result) <= 1, 'INVALID_PAGINATION_LINK')
    if result:
        require(result[0] != current, 'PAGINATION_LOOP')
        before, after = urlsplit(current).path, urlsplit(result[0]).path
        if before != after:
            require(identity is not None, 'PAGINATION_ENDPOINT_CHANGED')
            def suffix(path):
                numeric = re.fullmatch(r'/repositories/(\d+)(/.*)', path)
                named = re.fullmatch(r'/repos/([\w.-]+/[\w.-]+)(/.*)', path)
                if numeric and int(numeric[1]) == identity['provider_id']:
                    return numeric[2]
                if named and named[1].lower() in (identity['repository'].lower(), identity['canonical_name'].lower()):
                    return named[2]
                return None
            require(suffix(before) is not None and suffix(before) == suffix(after), 'PAGINATION_ENDPOINT_CHANGED')
    return result[0] if result else None


def retry_time(headers, now, attempts):
    values = [now + min(3600, 60 * 2 ** min(attempts - 1, 6))]
    if headers.get('retry-after'):
        try:
            values.append(now + float(headers['retry-after']))
        except ValueError:
            try:
                values.append(parsedate_to_datetime(headers['retry-after']).timestamp())
            except (ValueError, TypeError):
                pass
    if headers.get('x-ratelimit-remaining') == '0':
        try:
            values.append(float(headers['x-ratelimit-reset']) + 1)
        except (ValueError, KeyError):
            pass
    return max(values)


def save_source(c, job, item, kind, raw_blob, locator, now, origin):
    require(isinstance(item, dict), 'INVALID_RESOURCE_JSON')
    if kind == 'pr_file':
        require(isinstance(item.get('filename'), str) and isinstance(item.get('sha'), str), 'INVALID_FILE_METADATA')
        provider_id = f'pull:{json.loads(job["spec"])["parent_provider_id"]}:file:{item["filename"]}'
        text = item.get('patch', '')
    else:
        require(type(item.get('id')) is int and item['id'] > 0, 'MISSING_PROVIDER_ID')
        provider_id = str(item['id'])
        text = item.get('body') or ''
    require(isinstance(text, str), 'INVALID_BODY_TYPE')
    raw_item = c.put(canonical(item))
    body_blob = c.put(text.encode('utf-8'))
    row = c.db.execute('SELECT id FROM sources WHERE provider=? AND resource_kind=? AND provider_id=?',
                       ('github', kind, provider_id)).fetchone()
    source_id = row[0] if row else str(uuid.uuid4())
    if row is None:
        c.db.execute('INSERT INTO sources VALUES(?,?,?,?)', (source_id, 'github', kind, provider_id))
    require(origin in ('real', 'synthetic'), 'INVALID_ORIGIN')
    rid = c.record('source_revision', {'schema_version': 1, 'origin': origin, 'source_id': source_id,
                   'provider': 'github', 'resource_kind': kind, 'provider_id': provider_id,
                   'url': item.get('html_url') or item.get('url'), 'acquisition': 'github_http',
                   'provider_created_at': item.get('created_at'), 'provider_updated_at': item.get('updated_at'),
                   'content_available_at': None, 'historical_content': 'HISTORICAL_CONTENT_UNVERIFIED',
                   'body_blob': body_blob, 'resource_blob': raw_item,
                   'quality': 'PENDING', 'leakage': 'PENDING'}, [body_blob, raw_item])
    observation = c.record('source_observation', {'source_revision': rid, 'raw_blob': raw_blob,
                           'locator': locator, 'body_pointer': '/patch' if kind == 'pr_file' else '/body',
                           'observed_at': datetime.fromtimestamp(now, timezone.utc).isoformat(),
                           'collection_id': job['collection_id'], 'job_id': job['id'], 'attempt': job['attempts']},
                           [raw_blob], [rid])
    return observation


def process_page(c, job, plan, body, headers, raw_blob, now, origin='real'):
    data = json.loads(body)
    recipe, cid, role = plan['recipe'], job['collection_id'], job['role']
    spec = json.loads(job['spec'])
    refs, reason, state = [], None, 'SUCCEEDED'
    identity = c.db.execute('SELECT * FROM collection_repository_ids WHERE collection_id=? AND repository=?',
                            (cid, job['repository'])).fetchone()
    following = next_link(headers, job['url'], identity=identity)
    if role == 'versions':
        require(isinstance(data, list) and recipe['api_version'] in data, 'UNSUPPORTED_API_VERSION')
        return state, reason, refs
    if role == 'repository':
        require(isinstance(data, dict) and data.get('private') is False and type(data.get('id')) is int, 'REPOSITORY_NOT_PUBLIC')
        c.db.execute("UPDATE collection_repos SET state='PUBLIC' WHERE collection_id=? AND repository=?", (cid, job['repository']))
        c.db.execute('INSERT OR REPLACE INTO collection_repository_ids VALUES(?,?,?,?)',
                     (cid, job['repository'], data['id'], data.get('full_name') or job['repository']))
        return state, reason, refs
    if role == 'search':
        require(isinstance(data, dict) and type(data.get('total_count')) is int and data['total_count'] >= 0
                and type(data.get('incomplete_results')) is bool and isinstance(data.get('items'), list), 'INVALID_SEARCH_JSON')
        if data['total_count'] >= 1000 or data['incomplete_results']:
            start, end = date.fromisoformat(spec['start']), date.fromisoformat(spec['end'])
            partitions = c.db.execute("SELECT count(*) FROM collection_jobs WHERE collection_id=? AND role='search'", (cid,)).fetchone()[0]
            if (end - start).days >= 2 * recipe['limits']['min_partition_days'] and partitions + 2 <= recipe['limits']['search_partitions']:
                middle = start + (end - start) // 2
                for a, b in ((start, middle), (middle, end)):
                    sub = {**spec, 'start': a.isoformat(), 'end': b.isoformat(), 'page': 1}
                    queue(c, cid, search_url(sub), role, sub, job['repository'], priority=20)
                return 'SPLIT', 'SEARCH_CAP_OR_INCOMPLETE_SPLIT', refs
            state, reason = 'PARTIAL', 'SEARCH_CAP_OR_INCOMPLETE_UNRESOLVED'
        for item in sorted(data['items'], key=lambda x: digest(canonical([recipe['selection_seed'], x.get('id')]))):
            require(isinstance(item, dict) and type(item.get('id')) is int and type(item.get('number')) is int, 'INVALID_SEARCH_ITEM')
            if not add_target(c, cid, recipe, job['repository'], item['number'], lane=spec['lane']):
                state, reason = 'PARTIAL', 'RESOURCE_OR_LANE_LIMIT'
        if spec.get('round', 0) == 0 and following is None:
            again = {**spec, 'round': 1, 'page': 1}
            queue(c, cid, search_url(again), role, again, job['repository'], priority=20)
    elif role in ('issue', 'pull_request'):
        refs.append(save_source(c, job, data, role, raw_blob, '', now, origin))
        require(type(data.get('number')) is int and data['number'] == spec['number'], 'ISSUE_NUMBER_MISMATCH')
        base = f'https://api.github.com/repos/{job["repository"]}'
        if role == 'issue':
            if recipe['acquisition']['issue_comments']:
                queue(c, cid, f'{base}/issues/{spec["number"]}/comments?per_page=100', 'issue_comment',
                      {**spec, 'page': 1}, job['repository'], job['root'])
            if recipe['acquisition']['timeline']:
                queue(c, cid, f'{base}/issues/{spec["number"]}/timeline?per_page=100', 'timeline',
                      {**spec, 'page': 1}, job['repository'], job['root'])
            if data.get('pull_request'):
                url = f'{base}/pulls/{spec["number"]}'
                queue(c, cid, url, 'pull_request', spec, job['repository'], job['root'])
        else:
            for enabled, suffix, subrole in ((recipe['acquisition']['pr_reviews'], 'reviews', 'pr_review'),
                                             (recipe['acquisition']['pr_reviews'], 'comments', 'pr_review_comment'),
                                             (recipe['acquisition']['pr_files'], 'files', 'pr_file')):
                if enabled:
                    queue(c, cid, f'{base}/pulls/{spec["number"]}/{suffix}?per_page=100', subrole,
                          {**spec, 'page': 1, 'expected_files': data.get('changed_files'), 'parent_provider_id': data['id']}, job['repository'], job['root'])
    else:
        require(isinstance(data, list), 'INVALID_LIST_JSON')
        for index, item in enumerate(data):
            if role == 'timeline':
                require(isinstance(item, dict), 'INVALID_TIMELINE_EVENT')
                related = item.get('source', {}).get('issue') if isinstance(item.get('source'), dict) else None
                if item.get('event') == 'cross-referenced' and related:
                    url = related.get('html_url', '')
                    match = re.fullmatch(r'https://github\.com/([\w.-]+/[\w.-]+)/(?:pull|issues)/(\d+)', url)
                    acquired = False
                    deferred_reason = 'UNSUPPORTED_LINK_SHAPE' if not match else 'RELATED_DEPTH_LIMIT'
                    if match and spec.get('depth', 0) < recipe['acquisition']['related_depth']:
                        repo, number = match.groups()
                        deferred_reason = 'RELATED_REPOSITORY_SCOPE'
                        if repo.lower() in {x.lower() for x in plan['repositories']}:
                            acquired = add_target(c, cid, recipe, repo, int(number), spec.get('depth', 0) + 1)
                            deferred_reason = None if acquired else 'RESOURCE_LIMIT'
                    refs.append(c.record('source_relation_candidate', {'collection_id': cid, 'from_root': job['root'],
                                          'url': url, 'relation': 'cross_reference_not_same_incident',
                                          'acquired': acquired, 'deferred_reason': deferred_reason,
                                          'raw_blob': raw_blob, 'locator': f'/{index}'}, [raw_blob]))
            else:
                refs.append(save_source(c, job, item, role, raw_blob, f'/{index}', now, origin))
        # The files endpoint has a provider cap; never call a known truncated patch collection complete.
        if role == 'pr_file' and ((spec.get('expected_files') or 0) > 3000 or any('patch' not in item for item in data)):
            state, reason = 'PARTIAL', 'PR_PATCHES_INCOMPLETE_OR_BINARY'
        if not following and spec.get('round', 0) == 0:
            parsed = urlsplit(job['url'])
            query = urlencode([(k, v) for k, v in parse_qsl(parsed.query) if k != 'page'])
            first_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, ''))
            queue(c, cid, first_url, role, {**spec, 'round': 1, 'page': 1},
                  job['repository'], job['root'], job['priority'])
    if following:
        page = spec.get('page', 1)
        limit = recipe['limits']['search_pages' if role == 'search' else 'resource_pages']
        if page >= limit:
            state, reason = 'PARTIAL', 'PAGE_LIMIT'
        else:
            seen = c.db.execute('SELECT 1 FROM collection_jobs WHERE collection_id=? AND role=? AND url=? AND root=?',
                                (cid, role, following, job['root'])).fetchone()
            # Searches have two rounds; distinguish their repetition from pagination loops.
            if seen and role != 'search' and spec.get('round', 0) == 0:
                state, reason = 'PARTIAL', 'PAGINATION_LOOP'
            else:
                queue(c, cid, following, role, {**spec, 'page': page + 1}, job['repository'], job['root'], job['priority'])
    return state, reason, refs


def finish_response(c, job, plan, response, now, *, fail_at=None):
    recipe = plan['recipe']
    raw_blob = c.put(response.body)
    if fail_at == 'after_objects':
        raise CorpusError('Injected crash after object write')
    headers = {k.lower(): v for k, v in response.headers.items() if k.lower() in SAFE_HEADERS}
    cache_key = digest(canonical([job['url'], recipe['api_version']]))
    body, page_headers = response.body, headers
    code = response.error
    if len(body) > recipe['limits']['response_bytes']:
        code = 'RESPONSE_TOO_LARGE'
    if response.status == 304 and not code:
        cache = c.db.execute('SELECT * FROM collection_cache WHERE cache_key=?', (cache_key,)).fetchone()
        try:
            require(cache is not None, 'CACHE_MISSING')
            body = c.read(cache['body_blob'])
            page_headers = {**json.loads(cache['headers']), **headers}
            effective_blob = cache['body_blob']
        except CorpusError:
            code = 'CACHE_MISSING'
    else:
        effective_blob = raw_blob
    state, retry_at, refs = 'SUCCEEDED', 0, []
    rate_limited = response.status == 429 or (response.status == 403 and
                    (headers.get('x-ratelimit-remaining') == '0' or 'retry-after' in headers
                     or b'rate limit' in body.lower() or b'abuse' in body.lower()))
    if not code:
        if rate_limited:
            code = 'RATE_LIMITED'
        elif response.status in (301, 302, 307, 308):
            code = 'REDIRECT'
        elif response.status == 403:
            code = 'FORBIDDEN'
        elif response.status == 404:
            code = 'NOT_FOUND_OR_NOT_VISIBLE'
        elif response.status == 401:
            code = 'AUTHENTICATION_FAILED'
        elif response.status >= 500:
            code = 'SERVER_ERROR'
        elif response.status not in (200, 304):
            code = 'HTTP_ERROR'
    with c.transaction():
        check_lease(c, job, now)
        if code == 'CACHE_MISSING':
            c.db.execute('DELETE FROM collection_cache WHERE cache_key=?', (cache_key,))
        if code == 'REDIRECT':
            try:
                target = safe_url(urljoin(job['url'], headers.get('location', '')))
                require(target != job['url'], 'EMPTY_REDIRECT')
                require(json.loads(job['spec']).get('redirects', 0) < 3, 'REDIRECT_LIMIT')
                spec = json.loads(job['spec'])
                repository = job['repository']
                target_repo = re.match(r'^/repos/([\w.-]+/[\w.-]+)(?:/|$)', urlsplit(target).path)
                if job['role'] not in ('versions', 'repository') and target_repo and target_repo[1].lower() != repository.lower():
                    repository = target_repo[1]
                    add_repository(c, job['collection_id'], repository)
                numeric_repo = re.match(r'^/repositories/(\d+)(?:/|$)', urlsplit(target).path)
                if numeric_repo and job['role'] not in ('versions', 'repository'):
                    current_id = c.db.execute('SELECT provider_id FROM collection_repository_ids WHERE collection_id=? AND repository=?',
                                              (job['collection_id'], repository)).fetchone()
                    if current_id is None or current_id[0] != int(numeric_repo[1]):
                        c.db.execute("UPDATE collection_repos SET state='PENDING' WHERE collection_id=? AND repository=?",
                                     (job['collection_id'], repository))
                        queue(c, job['collection_id'], f'https://api.github.com/repositories/{numeric_repo[1]}',
                              'repository', repository=repository, priority=0)
                queue(c, job['collection_id'], target, job['role'], {**spec, 'redirects': spec.get('redirects', 0) + 1},
                      repository, job['root'], job['priority'])
                state, code = 'SPLIT', 'REDIRECT_FOLLOWED'
            except CorpusError:
                state, code = 'BLOCKED', 'UNSAFE_OR_EXCESSIVE_REDIRECT'
        elif code:
            retryable = code in ('TIMEOUT', 'TRANSPORT_ERROR', 'TRUNCATED_BODY', 'RATE_LIMITED', 'SERVER_ERROR', 'CACHE_MISSING')
            state = 'RETRY_WAIT' if retryable and job['attempts'] < recipe['http']['retry_attempts'] else 'FAILED_FINAL'
            if code == 'RESPONSE_TOO_LARGE':
                state = 'PARTIAL'
            retry_at = retry_time(headers, now, job['attempts']) if state == 'RETRY_WAIT' else 0
        else:
            # Roll back partial page processing on malformed JSON or a bad item.
            c.db.execute('SAVEPOINT page')
            try:
                state, code, refs = process_page(c, job, plan, body, page_headers, effective_blob, now, response.origin)
                c.db.execute('RELEASE page')
                c.db.execute('INSERT OR REPLACE INTO collection_cache VALUES(?,?,?)',
                             (cache_key, effective_blob, canonical(page_headers).decode()))
            except (ValueError, KeyError, TypeError, AttributeError) as e:
                c.db.execute('ROLLBACK TO page')
                c.db.execute('RELEASE page')
                state, code, refs = 'FAILED_FINAL', 'INVALID_JSON_OR_PAYLOAD', []
                if isinstance(e, CorpusError) and str(e) in ('UNSUPPORTED_API_VERSION', 'REPOSITORY_NOT_PUBLIC'):
                    state, code = 'BLOCKED', str(e)
        attempt = c.record('fetch_attempt', {'schema_version': 1, 'origin': response.origin, 'collection_id': job['collection_id'],
                           'job_id': job['id'], 'attempt': job['attempts'], 'fencing_token': job['token'],
                           'url': job['url'], 'method': 'GET', 'api_version': recipe['api_version'],
                           'observed_at': datetime.fromtimestamp(now, timezone.utc).isoformat(),
                           'status': response.status, 'headers': headers, 'raw_blob': raw_blob,
                           'effective_blob': effective_blob if not response.error and not (response.status == 304 and code == 'CACHE_MISSING') else None,
                           'outcome': state, 'reason': code}, [raw_blob, *([effective_blob] if response.status == 304 and code != 'CACHE_MISSING' else [])], refs)
        c.db.execute('UPDATE collection_jobs SET state=?,error=?,retry_at=?,result_id=?,lease_until=0 WHERE id=? AND token=?',
                     (state, code, retry_at, attempt, job['id'], job['token']))
        c.db.execute('UPDATE collections SET bytes=bytes-?+? WHERE id=?',
                     (recipe['limits']['response_bytes'], len(response.body), job['collection_id']))
        if rate_limited or headers.get('x-ratelimit-remaining') == '0':
            c.db.execute('UPDATE collections SET not_before=MAX(not_before,?) WHERE id=?',
                         (retry_time(headers, now, job['attempts']), job['collection_id']))
        if job['role'] == 'repository' and state in ('FAILED_FINAL', 'BLOCKED'):
            c.db.execute("UPDATE collection_repos SET state='BLOCKED' WHERE collection_id=? AND repository=?", (job['collection_id'], job['repository']))
        if fail_at == 'before_commit':
            raise CorpusError('Injected crash before page commit')
    if fail_at == 'after_commit':
        raise CorpusError('Injected response loss after page commit')


def collection_status(c, cid):
    cid = resolve_collection(c, cid)
    col = dict(c.db.execute('SELECT * FROM collections WHERE id=?', (cid,)).fetchone())
    plan = c.get(col['plan_id'], 'collection_plan')
    jobs = [dict(r) for r in c.db.execute('SELECT * FROM collection_jobs WHERE collection_id=? ORDER BY rowid', (cid,))]
    counts = dict(Counter(j['state'] for j in jobs))
    pending = any(j['state'] in ('PENDING', 'RUNNING', 'RETRY_WAIT') for j in jobs)
    incomplete = any(j['state'] in ('PARTIAL', 'BLOCKED', 'FAILED_FINAL') for j in jobs)
    state = 'INCOMPLETE' if pending or incomplete else 'COMPLETE_FOR_POLICY'
    roots = []
    for target in c.db.execute('SELECT root FROM collection_targets WHERE collection_id=? ORDER BY root', (cid,)):
        relevant = [j for j in jobs if j['root'] == target[0]]
        missing = [{'role': j['role'], 'state': j['state'], 'reason': j['error']} for j in relevant if j['state'] not in ('SUCCEEDED', 'SPLIT')]
        roots.append({'root': target[0], 'acquisition': 'partial' if missing else 'complete_for_policy', 'missing': missing})
    future = [j['retry_at'] for j in jobs if j['state'] == 'RETRY_WAIT']
    future += [j['lease_until'] for j in jobs if j['state'] == 'RUNNING']
    if col['not_before'] > time.time():
        future.append(col['not_before'])
    return {'collection_id': cid, 'plan_id': col['plan_id'], 'epoch': col['epoch'], 'state': state,
            'phase': 'PAUSED' if pending else ('FINISHED_WITH_LIMITS' if incomplete else 'FINISHED'),
            'unfinished_jobs': sum(counts.get(s, 0) for s in ('PENDING', 'RUNNING', 'RETRY_WAIT')),
            'stop_reason': col['stop_reason'], 'jobs': counts, 'requests_reserved': col['requests'],
            'bytes_used_or_reserved': col['bytes'], 'next_retry_at': min(future) if future else None,
            'resources': roots, 'complete_resources': sum(x['acquisition'] == 'complete_for_policy' for x in roots),
            'source_observations': c.db.execute('''SELECT count(DISTINCT links.target_id) FROM collection_jobs jobs
                JOIN record_links links ON links.record_id=jobs.result_id JOIN records records ON records.id=links.target_id
                WHERE jobs.collection_id=? AND records.kind='source_observation' ''', (cid,)).fetchone()[0],
            'coverage_claim': plan['coverage_claim'], 'legacy_deferred_by_policy': plan['legacy_deferred_by_policy'],
            'known_limits': ['Live search is rescanned once; absence is not proved.', 'No historical edit reconstruction.',
                             'Attachments are recorded only; code is not executed.', 'All collected material remains unreviewed.'],
            'problems': [{'job_id': j['id'], 'role': j['role'], 'reason': j['error'], 'state': j['state']}
                         for j in jobs if j['error']],
            'recipe': plan['recipe']}


def run_collection(c, cid, *, transport=None, max_requests=100, max_seconds=300, retry_failed=False,
                   clock=time.time, sleep=time.sleep, fail_at=None, progress=None):
    cid = resolve_collection(c, cid)
    col = c.db.execute('SELECT * FROM collections WHERE id=?', (cid,)).fetchone()
    plan = c.get(col['plan_id'], 'collection_plan')
    require(plan['implementation_hash'] == implementation_hash(), 'Collector changed; create a new plan or refresh')
    require(max_requests > 0 and max_seconds > 0, 'Invocation limits must be positive')
    recipe = plan['recipe']
    if retry_failed:
        with c.transaction():
            c.db.execute("UPDATE collection_jobs SET state='PENDING',attempts=0,retry_at=0 WHERE collection_id=? AND state IN ('FAILED_FINAL','BLOCKED')", (cid,))
            c.db.execute("UPDATE collection_repos SET state='PENDING' WHERE collection_id=? AND state='BLOCKED'", (cid,))
    transport = transport or GitHubHTTP()
    started, count, reason = clock(), 0, None
    while count < max_requests and clock() - started < max_seconds:
        job, reason = lease_job(c, cid, recipe, clock())
        if job is None:
            col = c.db.execute('SELECT * FROM collections WHERE id=?', (cid,)).fetchone()
            # Short pacing waits only. Rate-limit and retry waits are surfaced for resume.
            due = min(v for v in (col['next_core'], col['next_search']) if v > clock()) if any(v > clock() for v in (col['next_core'], col['next_search'])) else None
            if reason == 'NO_RUNNABLE_JOB' and due and due - clock() <= 3 and clock() - started + due - clock() < max_seconds:
                sleep(max(0.001, due - clock()))
                continue
            break
        cache_key = digest(canonical([job['url'], recipe['api_version']]))
        cache = c.db.execute('SELECT * FROM collection_cache WHERE cache_key=?', (cache_key,)).fetchone()
        etag = None
        if cache:
            try:
                c.read(cache['body_blob'])
                etag = json.loads(cache['headers']).get('etag')
            except CorpusError:
                c.db.execute('DELETE FROM collection_cache WHERE cache_key=?', (cache_key,))
        response = transport.get(job['url'], api_version=recipe['api_version'], etag=etag,
                                 max_bytes=recipe['limits']['response_bytes'],
                                 timeout=max(0.1, min(recipe['http']['timeout_seconds'], max_seconds - (clock() - started))))
        finish_response(c, job, plan, response, clock(), fail_at=fail_at)
        count += 1
        if progress and count % 10 == 0:
            progress({'collection_id': cid, 'requests_this_invocation': count,
                      'last_role': job['role'], 'last_http_status': response.status})
    if count >= max_requests:
        reason = 'INVOCATION_REQUEST_LIMIT'
    elif clock() - started >= max_seconds:
        reason = 'INVOCATION_TIME_LIMIT'
    c.db.execute('UPDATE collections SET stop_reason=? WHERE id=?', (reason, cid))
    report = collection_status(c, cid)
    with c.transaction():
        receipt = c.record('acquisition_revision', {'collection_id': cid, 'report': report}, records=[col['plan_id']])
    return {**report, 'acquisition_revision': receipt, 'requests_this_invocation': count}
