export function retry(fn: Function, attempts: number = 3, delay: number = 100) {
  return fn();
}
retry(() => 1);
retry(() => 1, 3);
retry(() => 1, 5, 200);
