# Reduced excerpt of Registry.inception? on failing_ref
# lib/zeitwerk/registry.rb
# pair is [abspath, loader]; pair.first drops which loader.

def inception?(cpath)
  if pair = inceptions[cpath]
    pair.first
  end
end
