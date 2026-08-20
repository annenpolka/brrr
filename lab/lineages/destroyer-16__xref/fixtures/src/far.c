#include <stdlib.h>
/* Force >24 insns between name materialization and bl getenv. */
int main(void) {
    register const char *n __asm__("x19") = "FAR_WINDOW_NAME";
    __asm__ volatile(
        "nop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\n"
        "nop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\n"
        "nop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\n"
        : "+r"(n)
        :
        : "memory"
    );
    getenv(n);
    return 0;
}
