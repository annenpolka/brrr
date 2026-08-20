#include <stdlib.h>
/* One-hop wrapper: name is not *getenv. Argument is already in x0. */
char *wrap_dup(const char *n) { return getenv(n); }
int main(void) {
    wrap_dup("WRAP_ENV_NAME");
    getenv("DIRECT_ENV_NAME");
    return 0;
}
