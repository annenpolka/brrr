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
