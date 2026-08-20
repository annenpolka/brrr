export function openFile(path, err) {
  throw new Error("open " + path + ": " + err);
}

export function done(body) {
  return body + "\nDone.";
}

export function stamp(ts, body) {
  return ts + " ERROR " + body;
}

export function spawn(cmd) {
  return "failed to spawn `" + cmd + "`";
}

export function fence(response) {
  return "```json\n" + response() + "\n```";
}

export function cleanedWrite(cleaned) {
  return cleaned + "\n";
}

export function failed(op, path, err) {
  return "failed " + op + " on " + path + " with " + err;
}
