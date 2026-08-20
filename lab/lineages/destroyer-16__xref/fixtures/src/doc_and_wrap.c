#include <stdlib.h>
static const char help[] __attribute__((used)) =
    "\nWRAP_ENV_NAME      : documented and getenv via wrapper\n"
    "DIRECT_ENV_NAME      : documented and getenv direct\n";
char *wrap_dup(const char *n) { return getenv(n); }
int main(void) {
    wrap_dup("WRAP_ENV_NAME");
    getenv("DIRECT_ENV_NAME");
    return 0;
}
