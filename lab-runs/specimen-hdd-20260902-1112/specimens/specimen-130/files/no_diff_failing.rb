# Reduced excerpt of no_diff? / artifact_cache_valid? on failing_ref
# Library/Homebrew/test_bot/test_formulae.rb
# 4f6e4df964fa22f12591ca4b27e9b52df34b9494
# Cache identity is formula path vs tap_git_revision. Local patches omitted.

      def no_diff?(formula, git_ref)
        return false unless repository.directory?
        @fetched_refs ||= T.let([], T.nilable(T::Array[String]))
        if @fetched_refs.exclude?(git_ref)
          test git.to_s, "-C", repository.to_s, "fetch", "origin", git_ref, ignore_failures: true
          @fetched_refs << git_ref if steps.fetch(-1).passed?
        end

        relative_formula_path = formula.path.relative_path_from(repository)
        !!system(git.to_s, "-C", repository.to_s, "diff", "--no-ext-diff", "--quiet", git_ref, "--",
                 relative_formula_path.to_s)
      end

      def artifact_cache_valid?(formula, formulae_dependents: false)
        sha = local_bottle_hash(formula.name, bottle_dir: artifact_cache)
          &.dig(formula.name, "formula", "tap_git_revision")
        return false if sha.blank?
        return false unless no_diff?(formula, sha)
        # ...
      end
