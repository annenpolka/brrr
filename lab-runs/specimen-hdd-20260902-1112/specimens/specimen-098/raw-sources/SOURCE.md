repository: pypa/pip
issue: https://github.com/pypa/pip/issues/12372
pr: https://github.com/pypa/pip/pull/12392
failing_ref (merge first parent): a15dd75d98884c94a77d349b800c7c755d8c34e4
fixed_ref (merge commit): 417ca92b439dba33d707b5da2493358863256bc3
pr_head: 83e41d90afd2bfe941b48e5f9f3ed22eab7d1146
second_parent: 83e41d90afd2bfe941b48e5f9f3ed22eab7d1146
merged_at: 2023-12-17T11:55:05Z
merged_by: sbidoul
pr_author: sanderr
changed_files: src/pip/_internal/resolution/resolvelib/factory.py, tests/functional/test_new_resolver.py, tests/functional/test_install_reqs.py
pr_title: Fixed bug in extras handling for link requirements
milestone: 23.3
scout_note: not specimen-031 pip empty extra. not specimen-080 extra marker fixture. not pipmark. Distinct leftover: extras-wrapped link candidate not reusable as the base the constraint looks up.
