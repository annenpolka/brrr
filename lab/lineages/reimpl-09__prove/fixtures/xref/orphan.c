#include <stdio.h>

/* Isolated env-shaped bytes, no getenv. Assay called these DUE; prove must not. */
static const char orphan[] __attribute__((used)) = "ORPHAN_ENV_NAME";
static const char secret[] __attribute__((used)) = "APP_SECRET_TOKEN";

int main(void) {
    puts(orphan);
    puts(secret);
    return 0;
}
