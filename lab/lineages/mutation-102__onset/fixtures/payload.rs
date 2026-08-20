// Quoting must survive both a macOS home with a space and a Linux home
// with an apostrophe. These strings are the spec of the quoter, not a
// recording of one machine.
let mac = "/Users/John Doe/.cargo/bin/kizu";
let linux = "/home/ev'an/kizu";
let textbook = "/home/user/project";
assert_eq!(quote(mac), "'/Users/John Doe/.cargo/bin/kizu'");
assert_eq!(cwd, Path::new("/home/user/project"));
