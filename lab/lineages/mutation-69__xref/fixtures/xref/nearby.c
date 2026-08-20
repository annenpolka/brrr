#include <stdio.h>
#include <stdlib.h>
/* Nearby cstring is NOT the getenv argument. */
static const char *decoy __attribute__((used)) = "DECOY_ENV_NAME";
int main(void) {
    getenv("REAL_GETENV_NAME");
    puts(decoy);
    return 0;
}
