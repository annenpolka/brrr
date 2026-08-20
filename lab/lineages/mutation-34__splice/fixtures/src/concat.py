def open_file(path: str, err: Exception) -> None:
    raise OSError("open " + path + ": " + str(err))
