#include <stdlib.h>
/* -O0 spills args; recover_regs does not track [sp]. */
char *spill_wrap(const char *a, const char *b, const char *c, const char *n) {
    (void)a;
    (void)b;
    (void)c;
    return getenv(n);
}
int main(void) {
    spill_wrap("A", "B", "C", "SPILL_ENV_NAME");
    return 0;
}
