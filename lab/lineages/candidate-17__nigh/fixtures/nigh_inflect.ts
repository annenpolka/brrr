export function more(flag: string): boolean {
  return flag === "has_more";
}

export const payload = {
  hasMore: true,
};

export const wire = "hasMore";
