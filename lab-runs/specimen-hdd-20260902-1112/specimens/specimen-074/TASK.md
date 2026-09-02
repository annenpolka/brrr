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
