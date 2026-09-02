repository: evanw/esbuild
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
