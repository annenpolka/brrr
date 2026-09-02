#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet (esbuild metafile uniqueKey leftover).

evanw/esbuild#2071 / PR 2091. metafile bytesInOutput keeps the 25-byte
uniqueKey placeholder identity after the linker substitutes the final
hashed filename (and publicPath). Distinct from webpack specimen-090
CSS module [contenthash] leftover. Distinct from PR 504 CSS JS-stub in
metafile.inputs. Distinct from #1357 leftover missing metafile on watch.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, with_state
from update_index import main as update_index

JOB_ID = "job-0325"
WORKER = "scout-job-0325"
TRIAL = "hdd-esbmeta"
START_N = 92


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 130):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id in 092-129")


def packet_for(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: evanw/esbuild
failing_ref: 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
fixed_ref: a375b372f5a4947c3e7d2af68301190a88bf83cd
source_issue: https://github.com/evanw/esbuild/issues/2071
source_pr: https://github.com/evanw/esbuild/pull/2091
mechanism_tags:
  - leftover-uniquekey-identity
  - metafile-bytesInOutput
  - css-url-file-loader
ecosystem: esbuild
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

esbuild's metafile `bytesInOutput` can keep the identity it had when a CSS `url()` (or JS `file`/`copy` loader import) still named a 25-byte uniqueKey placeholder, even after the linker has substituted the final hashed filename.

In-tree test `TestMetafileVeryLongExternalPaths` (`internal/bundler/bundler_default_test.go`). `NeedsMetafile: true`. `LoaderFile` / `LoaderCopy` / `LoaderCSS`. Code splitting on.

The file loader writes a placeholder, not the final path:

```
uniqueKey := fmt.Sprintf("%sA%08d", uniqueKeyPrefix, sourceIndex)
// uniqueKeyPrefix = base64(12 random bytes) = 16 chars
// + "A" + 8-digit index = 25 chars
ast.URLForCSS = uniqueKey + ignoredSuffix
```

The CSS printer emits `url(<uniqueKey>)`. The linker later substitutes the final relative path (plus `publicPath` if set) so the written CSS names e.g. `./444…99chars…-55DNWN2R.file`. `outputs.*.bytes` uses the substituted file. `inputs.*.bytesInOutput` is recorded earlier.

Case A — CSS with no `url()` (never file-loader):

```
esbuild style.css --bundle --outdir=out --metafile=meta.json
```

`metafile.outputs["out/style.css"].inputs["style.css"].bytesInOutput` tracks the printed CSS bytes. No uniqueKey placeholder exists. No leftover.

Case B — CSS `url()` of a short asset, no `publicPath`. Public report (`body {background-image: url(./image.svg);}`):

Printer CSS contains `url(<25-char uniqueKey>)`. Written CSS contains `url(image-WFRGLPG5.svg)` (or similar). On failing revision `0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff`:

```
"outputs": {
  "dist/index.css": {
    "inputs": { "styles.css": { "bytesInOutput": 61 } },
    "bytes": 94
  }
}
```

`bytesInOutput` is 61 (leftover uniqueKey identity). The substituted path is not folded. `bytes` (94) is the substituted file.

Case C — same CSS, `publicPath: "/some-long-public-path/"` (public report). Written CSS:

```
body { background-image: url(/some-long-public-path/image-WFRGLPG5.svg); }
```

`bytesInOutput` stays 61 (same leftover skip as "publicPath is config, not file"). Reporter's substituted length is 76. `--asset-names` that lengthens the final filename also does not move `bytesInOutput`.

Case D — in-tree 99-character asset name (watch the leftover vs substituted delta). `project/bytesInOutput should be at least 99.css`:

```
a { background: url(444…99 fours….file) }
```

Written CSS names `./444…-55DNWN2R.file`. On failing_ref the CSS output's metafile says `"bytesInOutput": 52` while `"bytes": 196`. The 52 is leftover uniqueKey-sized identity. A CSS-source-only change (no url) would move `bytesInOutput` with the source. This asset-name-only / substitution-only change does not.

The developer wants to know which identity `bytesInOutput` actually contained after substitution: leftover already-hashed uniqueKey length (same skip as "printer CSS, not final path"), omitted (same as case A / never-url'd), or a new count because the substituted `url(...)` bytes / `publicPath` changed.
""",
        observed="""# OBSERVED

Public evanw/esbuild issue 2071 (somebee, opened 2022-03-02, closed 2022-12-14). Public PR 2091 (haikyuu; closed not merged). Failing world: parent `0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff`. Fix commit `a375b372f5a4947c3e7d2af68301190a88bf83cd` (`fix #2071: remap bytesInOutput for substitutions; closes #2091`).

Issue body (failing observables):

> When you supply a `publicPath`, the bytesInOutput value is incorrect for css files. … `bytesInOutput` of styles.css is shorter than the real output, as it does not include the `/some-long-public-path` in the calculation.

Follow-up (still failing, no publicPath required):

> `bytesInOutput` is actually incorrect whether you supply a `publicPath` or not. As long as you have a `url(...)` somewhere in your css that imports a path using file-loader. … The `bytesInOutput` are not at all affected by `--asset-names`, `--public-path` or any other option that ends up changing the urls in the output css.

Reporter: introduced in v0.12.12; not present on v0.9.7. Minimal repo `somebee/esbuild-bytes-offset-bug`.

PR 2091 body (failing identity):

> Bytes in output is based on `len(compileResult.CSS)` which is the result of the printer. And it includes the hash inside the url instead of the actual path. Example: `div{ background: url(hashthats25characterslong); }`

In-tree on the failing revision, `generateChunkCSS` records:

```
jMeta.AddString(fmt.Sprintf("... \\"bytesInOutput\\": %d ...",
    len(compileResult.CSS)))
```

`compileResult.CSS` still contains `url(<uniqueKey>)`. Path substitution (`substituteFinalPaths` / `breakOutputIntoPieces`) runs later for the written file and for `outputs.*.bytes`. `jsonMetadataChunkCallback` only receives `finalOutputSize` for the outer `bytes` field. `bytesInOutput` is not remapped.

Snapshot `TestMetafileVeryLongExternalPaths` on failing_ref, CSS output:

```
"out/bytesInOutput should be at least 99.css": {
  "inputs": {
    "project/bytesInOutput should be at least 99.css": {
      "bytesInOutput": 52
    }
  },
  "bytes": 196
}
```

JS file-loader sibling on the same snapshot: `"bytesInOutput": 45` for the 99-char `.file` inside the JS output (leftover uniqueKey in `len(compileResult.JS)`).

This packet is not webpack/webpack#20938 / specimen-090 (CSS module `[contenthash]` leftover after a referenced PNG filename moves; `realContentHash: false`). Not esbuild PR 504 (CSS-from-JS stub leftover in `metafile.inputs` producing invalid JSON). Not #1357 (CLI `--metafile` omitted on watch rebuilds). Not #1186 (plugin `onEnd` metafile undefined after first watch build).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""# COMMANDS

```
# in-tree on failing_ref 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
# (not executed on this lab host)

# case A — CSS, never url() a file-loader asset
# esbuild style.css --bundle --outdir=out --metafile=meta.json
# bytesInOutput tracks printed CSS; no uniqueKey leftover

# case B — CSS url() + file loader, no publicPath
# body { background-image: url(./image.svg); }
# esbuild styles.css --bundle --outdir=dist --metafile=meta.json --loader:.svg=file
# printer CSS: url(<16-char prefix>A<8-digit index>)
# written CSS: url(image-<hash>.svg)
# failing_ref: bytesInOutput leftover uniqueKey length (public report: 61)
# failing_ref: outputs.*.bytes is substituted (public report: 94)

# case C — same as B with publicPath
# --public-path=/some-long-public-path/
# written CSS: url(/some-long-public-path/image-<hash>.svg)
# failing_ref: bytesInOutput still leftover 61
# reporter substituted length: 76

# case D — in-tree TestMetafileVeryLongExternalPaths
# go test ./internal/bundler -run TestMetafileVeryLongExternalPaths
# CSS entry: a { background: url(<99 fours>.file) }
# failing_ref snapshot: CSS bytesInOutput 52, bytes 196
# failing_ref snapshot: JS file-loader bytesInOutput 45 for the 99-char .file

# case E — never url() / never file-loader the asset
# no uniqueKey in that CSS/JS compileResult; no leftover bytesInOutput identity
```

Not executed on this lab host.
""",
        tree="""evanw/esbuild
  internal/bundler/bundler.go
  internal/bundler/linker.go
  internal/bundler/bundler_default_test.go
  internal/bundler/snapshots/snapshots_default.txt
""",
        source="""repository: evanw/esbuild
issue: https://github.com/evanw/esbuild/issues/2071
pr: https://github.com/evanw/esbuild/pull/2091
failing_ref (parent of remap commit): 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
fixed_ref (evanw remap commit; PR 2091 closed not merged): a375b372f5a4947c3e7d2af68301190a88bf83cd
pr_head: cdc0e36a5340c5d0fe8a4f2d2b80dbb686e74df9
pr_base: 71be8bc24e70609ab50a80e90a17a1f5770c89b5
merged_at: not merged; closed 2022-12-14T19:36:07Z when a375b372 landed
changed_files (fix commit): CHANGELOG.md, internal/bundler/linker.go, internal/bundler/snapshots/snapshots_default.txt, scripts/js-api-tests.js
pr_title: accurate bytesInOutput for css that includes urls
scout_note: not specimen-090 webpack CSS [contenthash] leftover after PNG filename move. not PR 504 CSS JS-stub leftover in metafile.inputs. not #1357 leftover missing CLI metafile on watch. Distinct leftover: metafile bytesInOutput still names uniqueKey-sized identity after linker substitutes final hashed path / publicPath.
""",
        answer_key="""KNOWN FIX (sealed): evanw/esbuild commit a375b372f5a4947c3e7d2af68301190a88bf83cd (closes PR 2091 / issue 2071).

bytesInOutput used len(compileResult.CSS) / len(compileResult.JS) while those slices still contained uniqueKey placeholders (fmt.Sprintf("%sA%08d", prefix, sourceIndex), 25 bytes). Path substitution for cyclic references happened later; only outputs.*.bytes was remapped. Repair: keep per-input output pieces, then accurateFinalByteCount walks pieces and adds len(final importPath) for asset/chunk substitutions (same paths as substituteFinalPaths, including publicPath). CSS and JS jsonMetadataChunkCallback now call that after finalRelPath is known. Snapshot TestMetafileVeryLongExternalPaths: CSS bytesInOutput 52 -> 142; JS file-loader 45 -> 135.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (never-url'd CSS moves bytesInOutput with source vs url()+file-loader leftover uniqueKey vs publicPath/long asset-names substituted bytes; outputs.bytes remapped vs inputs.bytesInOutput leftover; JS file-loader vs CSS url-token)
reproducibility: source-backed issue + public PR + pinned parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two metafile stores disagree after substitution; uniqueKey length vs final hashed path; publicPath is config but still appears in written CSS
ecosystem: esbuild / css / file-loader
mechanism_family: leftover-uniquekey-identity, metafile-bytesInOutput, css-url-file-loader

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "file_loader_uniquekey.go": """// Reduced excerpt of LoaderFile on failing_ref
// internal/bundler/bundler.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
// uniqueKeyPrefix is 16 chars (base64 of 12 random bytes).
// "%sA%08d" => 25-byte placeholder. CSS printer emits this, not the final path.

    case config.LoaderFile:
        uniqueKey := fmt.Sprintf("%sA%08d", args.uniqueKeyPrefix, args.sourceIndex)
        uniqueKeyPath := uniqueKey + source.KeyPath.IgnoredSuffix
        expr := js_ast.Expr{Data: &js_ast.EString{Value: helpers.StringToUTF16(uniqueKeyPath)}}
        ast := js_parser.LazyExportAST(args.log, source, js_parser.OptionsFromConfig(&args.options), expr, "")
        ast.URLForCSS = uniqueKeyPath
        result.file.inputFile.Repr = &graph.JSRepr{AST: ast}
        result.ok = true
        result.file.inputFile.UniqueKeyForAdditionalFile = uniqueKey
""",
            "css_bytesInOutput_leftover.go": """// Reduced excerpt of generateChunkCSS on failing_ref
// internal/bundler/linker.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
// bytesInOutput = len(compileResult.CSS) while CSS still contains uniqueKey.
// jsonMetadataChunkCallback only patches the outer "bytes" after substitution.

            // Include this file in the metadata
            if c.options.NeedsMetafile {
                if isFirstMeta {
                    isFirstMeta = false
                } else {
                    jMeta.AddString(",")
                }
                jMeta.AddString(fmt.Sprintf("\\n        %s: {\\n          \\"bytesInOutput\\": %d\\n        }",
                    helpers.QuoteForJSON(c.graph.Files[compileResult.sourceIndex].InputFile.Source.PrettyPath, c.options.ASCIIOnly),
                    len(compileResult.CSS)))
            }

    // End the metadata lazily. The final output size is not known until the
    // final import paths are substituted into the output pieces generated below.
    if c.options.NeedsMetafile {
        chunk.jsonMetadataChunkCallback = func(finalOutputSize int) helpers.Joiner {
            if !isFirstMeta {
                jMeta.AddString("\\n      ")
            }
            jMeta.AddString(fmt.Sprintf("},\\n      \\"bytes\\": %d\\n    }", finalOutputSize))
            return jMeta
        }
    }
""",
            "js_bytesInOutput_leftover.go": """// Reduced excerpt of generateChunkJS on failing_ref
// internal/bundler/linker.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
// Same leftover: metaByteCount[path] += len(compileResult.JS)
// while JS still contains uniqueKey for file-loader imports.

            if c.options.NeedsMetafile {
                path := c.graph.Files[compileResult.sourceIndex].InputFile.Source.PrettyPath
                if count, ok := metaByteCount[path]; ok {
                    metaByteCount[path] = count + len(compileResult.JS)
                } else {
                    metaOrder = append(metaOrder, compileResult.sourceIndex)
                    metaByteCount[path] = len(compileResult.JS)
                }
            }
""",
            "uniquekey_prefix.go": """// Reduced excerpt of generateUniqueKeyPrefix on failing_ref
// internal/bundler/bundler.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff

func generateUniqueKeyPrefix() (string, error) {
    var data [12]byte
    rand.Seed(time.Now().UnixNano())
    if _, err := rand.Read(data[:]); err != nil {
        return "", err
    }
    // This is 16 bytes and shouldn't generate escape characters when put into strings
    return base64.URLEncoding.EncodeToString(data[:]), nil
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  TestMetafileVeryLongExternalPaths
  project/bytesInOutput should be at least 99.css
    a { background: url(<99 fours>.file) }
  LoaderFile / LoaderCopy / LoaderCSS
  NeedsMetafile: true
  uniqueKey = prefix16 + "A" + 8-digit sourceIndex  (25 bytes)

Case A (never url() / never file-loader):
  CSS bytesInOutput tracks printed CSS source
  no uniqueKey placeholder
  no leftover

Case B (url() + file loader, no publicPath):
  printer CSS: url(<uniqueKey>)
  written CSS: url(image-<hash>.svg)
  failing_ref bytesInOutput leftover uniqueKey length (public report 61)
  failing_ref outputs.bytes substituted (public report 94)

Case C (url() + publicPath / long asset-names):
  written CSS includes /some-long-public-path/ or long [hash] name
  failing_ref bytesInOutput still leftover 61
  reporter substituted length 76
  --asset-names / --public-path do not move bytesInOutput

Case D (in-tree 99-char name; package still imported):
  CSS bytesInOutput leftover 52 vs bytes 196
  JS file-loader bytesInOutput leftover 45 for the 99-char .file

Case E (never url() the asset from CSS):
  no uniqueKey in that CSS compileResult
  no CSS bytesInOutput identity involving the asset

Not this packet:
  webpack CSS module [contenthash] leftover after PNG filename move (specimen-090 / webpack#20938)
  CSS-from-JS stub leftover in metafile.inputs (esbuild PR 504)
  leftover missing CLI metafile on watch rebuilds (#1357)
  plugin onEnd metafile undefined after first watch build (#1186)
""",
        },
    )


def _complete_and_enqueue(spec_id: str) -> str:
    note = {"launched": False, "reason": ""}

    def fn(state):
        job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == JOB_ID), None)
        if job is None:
            raise SystemExit(f"{JOB_ID} missing")
        if job.get("status") == "CLAIMED" and job.get("worker") == WORKER:
            complete(state, JOB_ID, result="ok", artifact=f"specimens/{spec_id}")
        elif job.get("status") == "DONE" and job.get("artifact") == f"specimens/{spec_id}":
            pass
        else:
            raise SystemExit(
                f"{JOB_ID} status={job.get('status')} worker={job.get('worker')} artifact={job.get('artifact')}"
            )
        ids = {s.get("id") for s in state.get("specimens") or []}
        if spec_id not in ids:
            state.setdefault("specimens", []).append({"id": spec_id})
        already = any(
            j.get("queue") == "READY_R1_DREAM"
            and j.get("specimen") == spec_id
            and j.get("status") in {"READY", "CLAIMED"}
            for j in state.get("ready_jobs") or []
        )
        if not already:
            enqueue(
                state,
                "READY_R1_DREAM",
                input_ref=f"seeds/{spec_id}.md trial={TRIAL}",
                expected_output="0001-dreamer.md",
                kill_condition="15m",
                estimated_cost="r1",
                priority_reason="esbuild metafile leftover uniqueKey in bytesInOutput; not webpack 090 / not PR 504",
                specimen=spec_id,
                lineage=TRIAL,
                phase="cambrian",
                extra={"trial": TRIAL},
            )
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        running_r1 = [
            t
            for t in state.get("machine_tasks") or []
            if t.get("kind") == "r1" and t.get("status") == "running"
        ]
        ready_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "READY"
        ]
        inflight = len(claimed_r1) + len(running_r1)
        if inflight >= 2:
            note["reason"] = (
                "dream.sh not launched; 2+ R1 already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
                + (";" if claimed_r1 and running_r1 else "")
                + ",".join(f"{t.get('id')}:{t.get('trial')}" for t in running_r1)
            )
        elif inflight:
            note["reason"] = (
                "dream.sh not launched; R1 already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
                + ",".join(f"{t.get('id')}:{t.get('trial')}" for t in running_r1)
            )
        elif any(j.get("lineage") != TRIAL for j in ready_r1):
            note["reason"] = (
                "dream.sh not launched; READY_R1_DREAM already queued: "
                + ",".join(
                    f"{j['id']}:{j.get('lineage')}"
                    for j in ready_r1
                    if j.get("lineage") != TRIAL
                )
            )
        else:
            note["reason"] = (
                "dream.sh not launched from scout; READY_R1_DREAM enqueued "
                f"trial={TRIAL} (coordinator owns dreamer slots)"
            )
        return spec_id

    with_state(fn)
    return note["reason"]


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        path = emit(packet_for(spec_id))
        seed = write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(spec_id)
        print(path)
        print(seed)
        print(f"enqueued READY_R1_DREAM trial={TRIAL} specimen={spec_id}")
        print(launch_note)
    except Exception:
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
