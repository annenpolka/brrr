export function boom(path: string, code: number): string {
  return `cannot read '${path}' (code ${code})`;
}
