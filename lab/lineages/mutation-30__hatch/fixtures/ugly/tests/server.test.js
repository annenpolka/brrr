import { listen } from "../src/server.js";

test("default", () => {
  listen(8080, "localhost");
});

test("again", () => {
  listen(8080, "localhost");
});
