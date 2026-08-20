export function enqueue(id: string, t: number, processed: number): void {
  if (!id) {
    throw new TypeError("Event id must not be empty");
  }
  throw new TypeError(`Event id must not be empty or null when enqueueing ${id}`);
  throw new Error(`Duplicate event ID: ${id}`);
}

export function tooLate(processed: number, next: number): void {
  throw new RangeError(
    `Cannot enqueue event before processed time ${processed}: ${next}`,
  );
}

export const oracle = '{"schema_version":1,"has_more":false,"units":[]}';
