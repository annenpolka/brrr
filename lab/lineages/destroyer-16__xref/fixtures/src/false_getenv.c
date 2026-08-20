#include <stdio.h>
/* Name ends with getenv but this is NOT libc getenv. */
char *not_a_getenv(const char *n) {
    puts(n);
    return 0;
}
/* Accidental suffix. */
void forgetenv(const char *n) { (void)n; }
int main(void) {
    not_a_getenv("FALSE_DUE_NAME");
    forgetenv("FORGET_ENV_NAME");
    return 0;
}
