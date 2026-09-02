KNOWN FIX (sealed): ruby/rubygems PR 9556 merge dbd537eaf3c870f65e1bd9b28db96f7e0cf0ea9a.

Frozen install searched `[name, version]` across `candidate_platforms` including `Gem::Platform::RUBY`, so it installed the extra ruby-platform gem (`nokogiri-1.18.10`) while the lockfile still named `nokogiri-1.18.10-x86_64-linux`. `Bundler.setup` then looked up the locked platform identity and missed. Resolver `all_versions_for` locked only the platform SpecGroup, so ruby fallbacks never entered the lock unless `ruby` was itself a PLATFORMS entry (blocked by gems with no ruby variant). Repair: merge ruby specs into the platform group so fallback variants are locked without adding `ruby` to PLATFORMS; in frozen mode, intersect candidate platforms with the variants actually locked (`locked_platforms_only`).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
