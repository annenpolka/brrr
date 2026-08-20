def open_file(path: str, err: Exception) -> None:
    raise OSError("open " + path + ": " + str(err))


def suffix_err(path: str, err: Exception) -> str:
    return path + ": " + str(err)


def done(response) -> str:
    return response() + "\nDone."
