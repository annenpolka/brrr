export function handle(action: { kind: string }) {
  if (action.kind === "action.never-built") {
    return "ghost";
  }
  if (action.kind === "action.resolved-beam") {
    return "beam";
  }
  return "other";
}
