#include <stdio.h>
#include <string.h>
extern char **environ;
int main(void) {
    const char *want = "WALK_ENV_NAME";
    for (char **e = environ; e && *e; e++) {
        if (strncmp(*e, want, 13) == 0 && (*e)[13] == '=') {
            puts(*e);
        }
    }
    return 0;
}
