#include <stdio.h>
#include <stdlib.h>

int main(void) {
    getenv("REAL_GETENV_NAME");
    puts("DECOY_ENV_NAME");
    return 0;
}
