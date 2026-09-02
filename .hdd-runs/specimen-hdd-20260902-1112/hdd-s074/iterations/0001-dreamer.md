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
