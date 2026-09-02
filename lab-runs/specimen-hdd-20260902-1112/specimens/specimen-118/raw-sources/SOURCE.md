repository: hashicorp/terraform
issue: none
pr: https://github.com/hashicorp/terraform/pull/37396
failing_ref (squash parent): dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3
fixed_ref (squash merge): 28cb1307393a2a6a0d1600955e17cd585e1aa7b8
merged_at: 2025-08-05T10:00:31Z
pr_author: dbanck
merged_by: dbanck
changed_files: internal/terraform/node_resource_abstract_instance.go, internal/terraform/context_apply2_test.go, internal/terraform/context_test.go, .changes/v1.13/BUG FIXES-20250804-162137.yaml
pr_title: Fix resource identity being dropped from state in certain cases
scout_note: not specimen-081 leftover IdentityJSON vs nil schema Decode. Distinct leftover: apply omits Identity from state object on destroy-error and mark-only update. job-0473 unique vs 081 tfident.
