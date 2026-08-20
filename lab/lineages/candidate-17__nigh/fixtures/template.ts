export function describeTick(kind: string): string {
  return `mode ${kind === "forced-slash" ? "Forced Slash" : "other"}`;
}

export function setTick(): string {
  let expectedTickKind = "forced-slash";
  return expectedTickKind;
}
