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
