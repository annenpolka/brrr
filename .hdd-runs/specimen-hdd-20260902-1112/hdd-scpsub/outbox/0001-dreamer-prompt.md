# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A git dependency's `.gitmodules` names a submodule with an **SCP-like** URL (`git@github.com:foo/bar.git`). That form is not a WHATWG URL. Cargo still has to build a `SourceId` (which requires `Url`) and then fetch.

On failing_ref `843a683fef61e9b3f9607ab637b72b0774241513`, `absolute_submodule_url` parses the child URL with `gix` and, when `serialize_alternative_form && scheme == Ssh`, turns alternative form **off** and serializes `ssh://git@host/path`. `update_submodule` then does `child_remote_url.into_url()` and `GitSource::new(source_id)`. `GitRemote` stores a `Url`. Fetch and user-facing messages therefore use the converted `ssh://` identity.

SCP-like `git@host:path` is relative to the user's home (`~/path`). `ssh://git@host/path` is absolute from `/path`. For GitHub/GitLab the two are intercepted the same; for a self-hosted server they are not.

In-tree `dep_with_scp_like_submodule_url` (`tests/testsuite/git.rs`): dependency `dep1` has submodule `submod` with `url = git@github.com:foo/bar.git`. `cargo fetch` with `GIT_SSH_COMMAND=false`. On this revision the `[UPDATING] git submodule` line and `failed to fetch submodule` line name `ssh://git@github.com/foo/bar.git`.

Case A — submodule URL is already `https://` or `ssh://host/path` (WHATWG):
  `into_url` succeeds without conversion
  fetch identity equals `.gitmodules` identity
  no leftover

Case B — submodule URL is SCP-like `git@github.com:foo/bar.git`:
  `absolute_submodule_url` emits `ssh://git@github.com/foo/bar.git`
  `GitSource::new` fetches that `Url`
  `.gitmodules` still names `git@github.com:foo/bar.git`
  leftover: converted ssh:// is the live fetch identity

Case C — relative submodule `./` / `../` against an SCP-like parent:
  failing_ref tests in `absolute_submodule_url` expect the converted `ssh://..././` form
  leftover conversion applies to the joined string

Case D — GitHub/GitLab host (both forms intercepted):
  fetch may succeed with either spelling
  leftover identity is still the ssh:// rewrite; path semantics happen to match

The developer wants to know, for case B, which identity `GitRemote` / fetch used: leftover `ssh://` converted from SCP-like, the original `.gitmodules` SCP-like string, or omitted.

# OBSERVED

Public rust-lang/cargo issue 16740 (weihanglo, closed 2026-03-13) and PR 16744 (weihanglo, merged 2026-03-13, merge `cbb9bb8bd0fb272b1be0d63a010701ecb3d1d6d3`). Failing world pinned on merge first parent `843a683fef61e9b3f9607ab637b72b0774241513`. Follow-up of #16727 (SCP-like URLs failed `Url::parse` with `relative URL without a base`). Local cargo execution was not performed on this lab host.

Issue body: after converting SCP-like to `ssh://` for parse, path semantics differ (`git@host:path` vs `ssh://git@host/path`). GitHub/GitLab hide it; a self-hosted `~/repos/foo.git` vs `/repos/foo.git` does not.

Failing_ref `absolute_submodule_url` always rewrites alternative SSH form to `ssh://`. `update_submodule` builds `SourceId::for_git(&child_remote_url.into_url()?)` and `GitSource::new`. `GitRemote.url` is `Url`. In-tree test `dep_with_scp_like_submodule_url` expects submodule lines to show `ssh://git@github.com/foo/bar.git`.

Not this packet: specimen-091 (RecursivePathSource PathBuf `..` duplicate package). specimen-005/024/086 cargo fingerprints. cargo#17289 checkout short-id vs core.abbrev. cargo#16727 (parse failure, not leftover fetch identity).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 843a683fef61e9b3f9607ab637b72b0774241513
# src/cargo/sources/git/utils.rs absolute_submodule_url / update_submodule
# tests/testsuite/git.rs dep_with_scp_like_submodule_url

# public shape:
# .gitmodules: url = git@github.com:foo/bar.git
# cargo fetch
# failing: [UPDATING] git submodule `ssh://git@github.com/foo/bar.git`
```

Source-backed only. Do not execute untrusted checkouts on the host.

rust-lang/cargo
  src/cargo/sources/git/utils.rs
  src/cargo/sources/git/source.rs
  tests/testsuite/git.rs

RELEVANT MATERIAL

### absolute_submodule_url_failing.rs

// Reduced excerpt of absolute_submodule_url on failing_ref
// src/cargo/sources/git/utils.rs
// 843a683fef61e9b3f9607ab637b72b0774241513
// SCP-like alternative form is serialized as ssh://.

    let absolute_url = match gix::url::parse(gix::bstr::BStr::new(absolute_url.as_ref().as_bytes()))
    {
        Ok(mut url) if url.serialize_alternative_form && url.scheme == gix::url::Scheme::Ssh => {
            url.serialize_alternative_form = false;
            Cow::from(url.to_bstring().to_string())
        }
        _ => absolute_url,
    };

    Ok(absolute_url)

### leftover_identity_split.txt

Fixture:
  git dependency dep1 with submodule submod
  .gitmodules url = git@github.com:foo/bar.git
  cargo fetch (GIT_SSH_COMMAND=false)

Case A (https or ssh:// WHATWG submodule URL):
  into_url succeeds
  fetch identity equals .gitmodules
  no leftover

Case B (SCP-like git@github.com:foo/bar.git):
  absolute_submodule_url emits ssh://git@github.com/foo/bar.git
  GitRemote stores that Url
  fetch and stderr use ssh://
  .gitmodules still names git@github.com:foo/bar.git
  leftover: converted ssh:// is the live fetch identity
  path semantics: SCP-like is home-relative; ssh:// is absolute /foo/bar.git

Case C (relative ./ or ../ against SCP-like parent):
  join then convert
  failing_ref tests expect ssh://..././ form

Case D (GitHub/GitLab intercept both spellings):
  leftover rewrite still happens; host hides the path split

Not this packet:
  cargo PathBuf .. duplicate package (specimen-091)
  cargo rustc_fingerprint (086)
  cargo#16727 parse failure before any fetch identity

### update_submodule_failing.rs

// Reduced excerpt of update_submodule on failing_ref
// src/cargo/sources/git/utils.rs
// Converted child_remote_url is parsed as Url and becomes GitSource/GitRemote.

            let child_remote_url = absolute_submodule_url(parent_remote_url, child_url_str)?;
            let reference = GitReference::Rev(head.to_string());

            let source_id = SourceId::for_git(&child_remote_url.into_url()?, reference)?
                .with_git_precise(Some(head.to_string()));

            let mut source = GitSource::new(source_id, gctx)?;
            let (db, actual_rev) = source.fetch_db(true).with_context(|| {
                let name = child.name().unwrap_or("");
                format!("failed to fetch submodule `{name}` from {child_remote_url}",)
            })?;

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
