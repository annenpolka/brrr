export type Phase = "idle" | "running" | "done" | "unknown";

export function tick(phase: Phase): number {
  if (phase === "done") {
    return 1;
  }
  return 0;
}

export function built(): Phase[] {
  return ["idle", "running", "unknown"];
}
