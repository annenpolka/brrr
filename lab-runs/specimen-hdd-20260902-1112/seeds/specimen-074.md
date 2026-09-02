CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Frozen `bundle install` on a lockfile that only lists a platform-specific gem succeeds, then `Bundler.setup` cannot find that gem.

Lockfile (only this variant):

```
GEM
  remote: https://gem.repo4/
  specs:
    nokogiri (1.18.10-x86_64-linux)

PLATFORMS
  x86_64-linux
```

The locked `x86_64-linux` package declares `required_ruby_version` strictly less than the running Ruby. Same machine, `BUNDLE_FROZEN=true`:

```
bundle install --verbose
# Fetching nokogiri 1.18.10
# Installing nokogiri 1.18.10
# exit 0

ruby -e "require 'bundler'; Bundler.setup"
# Could not find nokogiri-1.18.10-x86_64-linux in locally installed gems
# exit nonzero
```

The developer wants to know which gem identity install actually materialized, and which identity setup later searched for.

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

# COMMANDS

```
# lockfile has only: nokogiri (1.18.10-x86_64-linux)
# that variant's required_ruby_version is < running Ruby
BUNDLE_FROZEN=true bundle install --verbose
# Fetching nokogiri 1.18.10
# Installing nokogiri 1.18.10

BUNDLE_FROZEN=true ruby -e "require 'bundler'; Bundler.setup"
# Could not find nokogiri-1.18.10-x86_64-linux in locally installed gems
```

Not executed on this lab host.

ruby/rubygems
  bundler/lib/bundler/lazy_specification.rb
  bundler/lib/bundler/resolver.rb
  spec/install/gemfile/specific_platform_spec.rb

RELEVANT MATERIAL

### all_versions_for_failing.rb

# Reduced excerpt of Resolver#all_versions_for on failing_ref
# bundler/lib/bundler/resolver.rb

ruby_specs = MatchPlatform.select_best_platform_match(specs, Gem::Platform::RUBY)
ruby_group = Resolver::SpecGroup.new(ruby_specs)

unless ruby_group.empty?
  platform_specs.each do |s|
    ruby_group.merge(Resolver::SpecGroup.new(s))
  end

  groups << Resolver::Candidate.new(version, group: ruby_group, priority: -1)
  next groups if package.force_ruby_platform?
end

platform_group = Resolver::SpecGroup.new(platform_specs.flatten.uniq)
next groups if platform_group == ruby_group

groups << Resolver::Candidate.new(version, group: platform_group, priority: 1)

### frozen_install_setup.txt

Lockfile (failing world):
  specs:
    nokogiri (1.18.10-x86_64-linux)
  PLATFORMS
    x86_64-linux

Published index:
  nokogiri-1.18.10                 (ruby; installable on current Ruby)
  nokogiri-1.18.10-x86_64-linux    (required_ruby_version < running Ruby)

BUNDLE_FROZEN=true bundle install --verbose
  Fetching nokogiri 1.18.10
  Installing nokogiri 1.18.10
  exit 0

BUNDLE_FROZEN=true ruby -e "require 'bundler'; Bundler.setup"
  Could not find nokogiri-1.18.10-x86_64-linux in locally installed gems
  exit nonzero

### materialize_for_installation_failing.rb

# Reduced excerpt of LazySpecification on failing_ref
# bundler/lib/bundler/lazy_specification.rb

def full_name
  @full_name ||= if platform == Gem::Platform::RUBY
    "#{@name}-#{@version}"
  else
    "#{@name}-#{@version}-#{platform}"
  end
end

def materialize_for_installation
  source.local!

  if use_exact_resolved_specifications?
    spec = materialize(self) {|specs| choose_compatible(specs, fallback_to_non_installable: false) }
    return spec if spec

    # Exact spec is incompatible; in frozen mode, try to find a compatible platform variant
    # In non-frozen mode, return nil to trigger re-resolution and lockfile update
    if Bundler.frozen_bundle?
      materialize([name, version]) {|specs| resolve_best_platform(specs) }
    end
  else
    materialize([name, version]) {|specs| resolve_best_platform(specs) }
  end
end

def candidate_platforms
  target = source.is_a?(Source::Path) ? platform : Bundler.local_platform
  [target, platform, Gem::Platform::RUBY].uniq
end

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
