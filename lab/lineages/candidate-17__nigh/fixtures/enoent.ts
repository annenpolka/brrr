export function missing(error: { code: string }): boolean {
  return error.code === "ENOENT";
}

export const logicalEventId = "event";
