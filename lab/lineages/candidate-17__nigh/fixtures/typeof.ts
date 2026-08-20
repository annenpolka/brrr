export function asString(x: unknown): string {
  if (typeof x === "string") {
    return x;
  }
  if (typeof x === "object") {
    return "obj";
  }
  return "other";
}

export const kind = "beam";
