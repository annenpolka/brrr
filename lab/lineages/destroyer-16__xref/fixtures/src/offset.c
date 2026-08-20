#include <stdlib.h>
/* CPython _env_to_dict shape: getenv(&"ENV_NAME"[4]). */
char *env_to(const char *key) { return getenv(key + 4); }
int main(void) {
    env_to("ENV_OFFSET_NAME");
    return 0;
}
