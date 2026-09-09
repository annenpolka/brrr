#!/usr/bin/env python3
"""Prepare an original issue's reported input files. Does not approve or run source code."""
import argparse
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from brrr_corpus.cases import reprocess, save_case, save_claim
from brrr_corpus.catalog import review_package, sources, show_source
from brrr_corpus.mini import add_prompt, recipe_file
from brrr_corpus.selection import build_selection
from brrr_corpus.store import Corpus, CorpusError, canonical, publish_tree, require


def prepare(root, output):
    require((Path(root) / 'corpus.sqlite').is_file(), 'Collect mini-evidence-v1 first')
    c = Corpus(root)
    try:
        found = sources(c, limit=1000)
        require(not found['truncated'], 'Small example source limit exceeded')
        originals = [s for s in found['matches'] if s['kind'] == 'issue' and s['url'] == 'https://github.com/denoland/deno/issues/32113']
        require(len(originals) == 1, 'Choose an explicit original revision after refresh')
        original = originals[0]['revision']
        raw = c.read(c.get(original)['body_blob'])
        require(raw.startswith(b'Version: Deno 2.6.8\n'), 'Report version changed; review extraction again')
        blocks = list(re.finditer(rb'```\n(.*?)```', raw, re.DOTALL))
        require(len(blocks) == 3, 'Report structure changed; review extraction again')
        require(json.loads(blocks[0][1]) == {'dependencies': {'': '.'}}, 'Reported package input changed')
        require(blocks[1][1].startswith(b'import { it } from "jsr:@std/testing/bdd";'), 'Reported JS changed')
        related_roots = {f'https://github.com/denoland/deno/pull/{i}' for i in (33094,33243,34009,34514)}
        refs, mixed, forbidden, overlap_records = [], [], set(related_roots), []
        symptom = b"Invalid workspace section: Invalid package requirement '@.'"
        for item in found['matches']:
            url = item['url'].split('#')[0]
            if url not in related_roots and url != originals[0]['url'] and not related_roots.intersection(item['related_pull_urls']):
                continue
            source = show_source(c, item['revision'])
            body = source['body'].encode('utf-8')
            classification = 'candidate_public' if item['revision'] == original else 'restricted_solution'
            # Two proposed-fix descriptions quote this exact original symptom on its own line.
            # Keep the entire descriptions private, but classify that redundant symptom separately
            # from the causal/fix spans so an exact-match scan does not erase reported evidence.
            standalone = re.search(rb'(?m)^' + re.escape(symptom) + rb'\r?$', body)
            if item['revision'] != original and standalone:
                require(symptom in raw, 'Overlap is not original reported evidence')
                classification = 'unreviewed'
                mixed.append((item['revision'], standalone.start(), standalone.end(), len(body)))
            refs.append({'revision': item['revision'], 'classification': classification})
            if item['revision'] != original:
                if item['url']:
                    forbidden.add(item['url'])
                m = source['resource'] or {}
                for field in ('title','filename','path','merge_commit_sha','commit_id'):
                    if m.get(field):
                        forbidden.add(m[field])
        require(len(refs) >= 10, 'Solution/review context is incomplete for this example')
        case_spec = {'key':'mini-evidence/repeated-run','title':'Reported first/second invocation difference',
                     'repository':'denoland/deno','origin':'real','sources':refs,'primary_mechanism':'unknown',
                     'exposure':'unknown','legacy_revisions':[],'forbidden_identifiers':sorted(forbidden)}
        case = save_case(c, case_spec)
        def quote(rid,start,end,classification='candidate_public', rationale='Exact range from the reported source; not locally executed.'):
            return save_claim(c, {'case_revision':case['case_revision'],'classification':classification,
                'segment':{'kind':'reporter_observation','source_revision':rid,'start':start,'end':end},'rationale':rationale})
        for rid,start,end,size in mixed:
            restricted = []
            if start: restricted.append(quote(rid,0,start,'restricted_solution','Proposed-fix context before the verbatim original diagnostic.'))
            if end<size: restricted.append(quote(rid,end,size,'restricted_solution','Proposed-fix context after the verbatim original diagnostic.'))
            overlap_records.append({'source_revision':rid,'private_quoted_symptom_range':[start,end],
                                    'original_revision':original,'original_range':[raw.index(symptom),raw.index(symptom)+len(symptom)],
                                    'restricted_claims':restricted,'publication_source':'original issue only; no PR text used'})
        version = quote(original,0,raw.index(b'\n'))
        package = quote(original,blocks[0].start(1),blocks[0].end(1))
        script = quote(original,blocks[1].start(1),blocks[1].end(1))
        logstart,logend = blocks[2].start(1),blocks[2].end(1)
        pathstart = raw.index(b'/Users/',logstart)
        pathend = raw.index(b"'",pathstart)
        before = quote(original,logstart,pathstart)
        after = quote(original,pathend,logend)
        redaction = add_prompt(c,case['case_revision'],'[reporter-local-path-omitted]')
        command = b'deno run a.js'
        cmd_start = raw.index(command,logstart)
        cmd = quote(original,cmd_start,cmd_start+len(command))
        framing = add_prompt(c,case['case_revision'],
            '\n\nReported input: package.json and a.js are copied verbatim under files/. The transcript reports two invocations of the same command with different outcomes.\n'
            'Investigation question: what state would you inspect or compare between these invocations to explain the reported difference, without assuming its cause?\n'
            'Unavailable: the generated deno.lock, resolved version of the unpinned JSR import, exact working-directory inventory, cache state and full OS/runtime build details. '
            'These files and outputs were reported, not executed or reproduced by this collector. The absolute path in the transcript is replaced by [reporter-local-path-omitted].\n'
            'Use the supplied files as the reported inputs. Additional files or command outcomes must not be presented as verified repository facts.\n')
        commands = add_prompt(c,case['case_revision'],
            '\n\nThe source reports the command above twice, with the transcript in OBSERVED.md. '
            'The supplied input files are in files/; no complete working directory or generated lockfile was supplied. '
            'No command has been run here. No success on a currently installed Deno version is claimed.\n')
        config = {'case_revision':case['case_revision'],'pipeline_id':'mini-evidence-v1','split':'discovery',
                  'sections':{'TASK.md':[version,framing],'OBSERVED.md':[before,redaction,after],
                              'COMMANDS.md':[cmd,commands],'files/package.json':[package],'files/a.js':[script]}}
        recipe=recipe_file('recipes/selection/mini-evidence-v1.json')
        result=reprocess(c,config,recipe['view_recipe'])
        package_result=review_package(c,result['view_id'],Path(output)/'review')
        selection=build_selection(c,recipe)
        receipt={**result,**case,'original_revision':original,'source_count':len(refs),
                 'overlap_classification':overlap_records,'selection_id':selection['selection_id'],
                 'selection_status':selection['status'],'review_package':package_result}
        publish_tree(Path(output)/'inputs',{'case.json':canonical(case_spec),'reprocess.json':canonical(config),
                     'view-recipe.json':canonical(recipe['view_recipe']),'receipt.json':canonical(receipt)})
        return receipt
    finally:
        c.close()


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default='.brrr-corpus/mini-followup')
    p.add_argument('--output',required=True)
    a=p.parse_args()
    try:
        print(json.dumps(prepare(a.root,a.output),ensure_ascii=False,indent=2))
    except (CorpusError,OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps({'ok':False,'error':str(error)}),file=sys.stderr)
        sys.exit(1)
