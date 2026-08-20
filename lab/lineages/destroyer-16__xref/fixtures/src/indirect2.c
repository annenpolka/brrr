#include <stdlib.h>
int main(void) {
    char *(*volatile f)(const char *) = getenv;
    f("INDIRECT_ENV_NAME");
    return 0;
}
