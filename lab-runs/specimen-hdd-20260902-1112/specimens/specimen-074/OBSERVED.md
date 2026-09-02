# OBSERVED

Public ruby/rubygems PR 9556. Failing world in `bundler/lib/bundler/lazy_specification.rb` and `bundler/lib/bundler/resolver.rb` around merge parent `b715e9cf3c2b285130ab968239c2231d5287a213`.

Two published gems share name and version:

```
nokogiri-1.18.10                 # Gem::Platform::RUBY (no platform suffix)
nokogiri-1.18.10-x86_64-linux    # platform-specific; required_ruby_version < running Ruby
```

`LazySpecification#full_name` is `#{name}-#{version}` on the ruby platform and `#{name}-#{version}-#{platform}` otherwise.

On the failing revision, frozen materialization of an exact locked spec that is metadata-incompatible does:

```
if Bundler.frozen_bundle?
  materialize([name, version]) {|specs| resolve_best_platform(specs) }
end
```

The search key is `[name, version]`, not the locked platform tuple. `resolve_best_platform` walks `candidate_platforms`:

```
def candidate_platforms
  target = source.is_a?(Source::Path) ? platform : Bundler.local_platform
  [target, platform, Gem::Platform::RUBY].uniq
end
```

`Gem::Platform::RUBY` is always in that list. Install therefore fetches and installs `nokogiri 1.18.10` (ruby platform). A PR demonstration of this revision records:

```
expect(exitstatus).to eq(0)
expect(out).to include("Fetching nokogiri 1.18.10\n")
expect(out).to include("Installing nokogiri 1.18.10\n")
# FIXME: We should not install an alternative and then refuse to use it.
ruby "require 'bundler'; Bundler.setup", env: { "BUNDLE_FROZEN" => "true" }
expect(err).to include("Could not find nokogiri-1.18.10-x86_64-linux in locally installed gems")
```

`Resolver#all_versions_for` builds a ruby group and a platform group separately. The candidate that wins for `x86_64-linux` is the platform group only:

```
platform_group = Resolver::SpecGroup.new(platform_specs.flatten.uniq)
next groups if platform_group == ruby_group
groups << Resolver::Candidate.new(version, group: platform_group, priority: 1)
```

The resulting lockfile line is `nokogiri (1.18.10-x86_64-linux)` with `PLATFORMS` still `x86_64-linux`. Gems that have no ruby variant (example used in-tree: `sorbet-static`) prevent adding `ruby` itself to `PLATFORMS`.

This packet does not include a local clone; treat the snippets and install/setup split as the world. Do not execute untrusted checkouts on the host.
