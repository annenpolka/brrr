#include <stdlib.h>
/* Second hop: even a one-hop wrapper follow misses this. */
char *hop1(const char *n) { return getenv(n); }
char *hop2(const char *n) { return hop1(n); }
int main(void) {
    hop2("HOP2_ENV_NAME");
    return 0;
}
