export function openFile(path, err) {
  throw new Error("open " + path + ": " + err);
}

export function suffixErr(path, err) {
  throw new Error(path + ": " + err);
}

export function done(response) {
  return response() + "\nDone.";
}
