#include <stdio.h>
__attribute__((noinline, used))
char *not_a_getenv(const char *n) {
    volatile const char *p = n;
    puts((char *)p);
    return 0;
}
__attribute__((noinline, used))
void forgetenv(const char *n) {
    volatile const char *p = n;
    (void)p;
}
int main(void) {
    not_a_getenv("FALSE_DUE_NAME");
    forgetenv("FORGET_ENV_NAME");
    return 0;
}
