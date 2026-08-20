#include <stdlib.h>
int main(void) {
    setenv("SETENV_ONLY_NAME", "1", 1);
    return 0;
}
