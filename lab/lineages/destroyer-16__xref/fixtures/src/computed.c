#include <stdlib.h>
#include <string.h>
int main(void) {
    char buf[32];
    memcpy(buf, "COMPUTED_ENV_NAME", 18);
    getenv(buf);
    return 0;
}
