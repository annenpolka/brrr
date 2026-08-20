#include <stdio.h>
/* Isolated env-shaped cstring. Nobody getenv()s it. */
static const char *msg __attribute__((used)) = "ORPHAN_ENV_NAME";
static const char *also __attribute__((used)) = "APP_SECRET_TOKEN";
int main(void) {
    puts(msg);
    puts(also);
    return 0;
}
