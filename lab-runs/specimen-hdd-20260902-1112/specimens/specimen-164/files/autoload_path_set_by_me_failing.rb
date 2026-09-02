# Reduced excerpt of autoload_path_set_by_me_for? on failing_ref
# lib/zeitwerk/loader.rb
# 8100bd18a42c29740e2d30d21b5f68be67f27d1b
# leftover gem inception path JOIN as this loader's autoload.

private def autoload_path_set_by_me_for?(cref)
  if autoload_path = cref.autoload?
    autoload_path if autoloads.key?(autoload_path)
  else
    Registry.inception?(cref.path)
  end
end
