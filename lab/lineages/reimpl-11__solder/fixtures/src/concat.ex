def open_file(path, err) do
  raise "open " <> path <> ": " <> err
end

def suffix_err(path, err) do
  raise path <> ": " <> err
end
