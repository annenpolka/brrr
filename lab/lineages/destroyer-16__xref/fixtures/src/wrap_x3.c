#include <stdlib.h>
/* CPython _config_get_env_dup shape: name in x3. */
char *wrap_x3(const char *a, const char *b, const char *c, const char *n) {
    (void)a;
    (void)b;
    (void)c;
    return getenv(n);
}
int main(void) {
    wrap_x3("A", "B", "C", "WRAP_X3_NAME");
    return 0;
}
