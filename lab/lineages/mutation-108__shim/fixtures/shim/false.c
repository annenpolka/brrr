#include <stdio.h>
#include <stdlib.h>

/* Suffix *getenv is not a getenv proof. These symbols must not DUE. */
__attribute__((noinline)) char *not_a_getenv(const char *n) {
    puts(n);
    return 0;
}

__attribute__((noinline)) void forgetenv(const char *n) { (void)n; }

int main(void) {
    not_a_getenv("FALSE_DUE_NAME");
    forgetenv("FORGET_ENV_NAME");
    getenv("REAL_GETENV_NAME");
    return 0;
}
