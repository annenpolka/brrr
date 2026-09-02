repository: ruby/ruby
issue: https://bugs.ruby-lang.org/issues/15790
pr: https://github.com/ruby/ruby/pull/4715
failing_ref (parent): ded5a66cb994c5731a17bc9a2420042248a2f1fe
fixed_ref (rb_const_remove after fail): 08759edea8fb75d46c3e75217e6613465426a0d2
merged_at: 2021-10-08T21:54:26Z
pr_author: jeremyevans
merged_by: nobu
changed_files: variable.c, test/ruby/test_autoload.rb, spec/ruby/core/module/autoload_spec.rb, spec/ruby/core/module/const_set_spec.rb
pr_title: Remove autoload for constant if the autoload fails
scout_note: not 054/110/157/159. leftover same-name helper vs moved definition after autoload fail. unique vs 001-163.
