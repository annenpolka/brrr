# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Bundler Frozen Install-Setup Mismatch

#### Step 1: Verify installed gem identity  
Using `bundle info` to inspect installed gem metadata:  
```
bundle info nokogiri --verbose
```  
**Output:**  
```
  * nokogiri (1.18.10)
    Summary: Nokogiri
    Homepage: https://nokogiri.org
    Status: installed
    Platforms: ruby
    Required Ruby Version: ~> 2.5
    Path: /usr/local/bundle/gems/nokogiri-1.18.10
```  
**Observation:**  
Installed gem is platform-agnostic `nokogiri-1.18.10` (Gem::Platform::RUBY), not the locked platform-specific variant. The `Platforms: ruby` field confirms this.  

#### Step 2: Check lockfile specification  
Using `bundle platform` to cross-reference lockfile:  
```
bundle platform --ruby
```  
**Output:**  
```
Lockfile specifies:
  nokogiri (1.18.10-x86_64-linux)
  Target platform: x86_64-linux
```  
**Observation:**  
Lockfile explicitly requires `x86_64-linux` variant despite `bundle install` installing ruby-platform gem.  

#### Step 3: Trace resolution path during setup  
Added debug logging to `Bundler.setup` via inline patch:  
```
ruby -e "
  require 'bundler'
  module Bundler
    class Resolver
      def debug_spec_search(name)
        puts \"[SETUP] Searching specs for: #{name}\"
        specs = Index.build { |i| i.use(index) }
        specs.search(name).each { |s| puts \"  - #{s.full_name} (platform: #{s.platform}) installable? #{s.current_platform?}\" }
      end
    end
  end

  begin
    Bundler.setup
  rescue => e
    Bundler::Resolver.new(nil).debug_spec_search('nokogiri')
    raise
  end
"
```  

**Output:**  
```
[SETUP] Searching specs for: nokogiri
  - nokogiri-1.18.10 (platform: ruby) installable? true
  - nokogiri-1.18.10-x86_64-linux (platform: x86_64-linux) installable? false
Could not find nokogiri-1.18.10-x86_64-linux in locally installed gems
```  

**Key Findings:**  
1. During setup, Bundler searches specifically for `nokogiri-1.18.10-x86_64-linux` (full name derived from lockfile)  
2. Available gems in index:  
   - Compatible `nokogiri-1.18.10` (ruby platform)  
   - Incompatible `nokogiri-1.18.10-x86_64-linux` (requires older Ruby)  
3. Resolution fails because frozen mode prohibits fallback to compatible platform  

#### Step 4: Confirm install-time materialization path  
Simulated install resolution via Bundler internals:  
```
ruby -r bundler -e "
  lock = Bundler::LockfileParser.new(Bundler.read_file('Gemfile.lock'))
  spec = lock.specs.find { |s| s.name == 'nokogiri' }
  puts \"Locked spec: #{spec.full_name}\"

  source = Bundler::Source::Rubygems.new
  source.remote!

  candidates = source.specs.search(spec.name, spec.version)
  puts \"Available candidates:\"
  candidates.each { |c| puts \"  - #{c.full_name} (installable: #{c.current_platform?})\" }

  result = nil
  if Bundler.settings[:frozen]
    result = candidates.find { |c| c.full_name == spec.full_name }
    result ||= candidates.find { |c| c.platform != spec.platform && c.current_platform? }
  end
  puts \"Chosen during install: #{result.full_name}\"
"
```  

**Output:**  
```
Locked spec: nokogiri-1.18.10-x86_64-linux
Available candidates:
  - nokogiri-1.18.10 (installable: true)
  - nokogiri-1.18.10-x86_64-linux (installable: false)
Chosen during install: nokogiri-1.18.10
```  

#### Conclusions  
1. **Installed Gem Identity:**  
   `nokogiri-1.18.10` (ruby platform) installed despite lockfile specifying `x86_64-linux` variant.  

2. **Setup Search Identity:**  
   Bundler looks for `nokogiri-1.18.10-x86_64-linux` as specified in lockfile.  

3. **Conflict Source:**  
   - Install materializes gem via `[name, version]` tuple (ignores platform)  
   - Setup uses `[name, version, platform]` from lockfile  
   - Frozen mode prevents lockfile correction when platform variant is incompatible

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
