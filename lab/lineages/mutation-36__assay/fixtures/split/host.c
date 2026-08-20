#include <stdio.h>
#include <stdlib.h>

/* Keep the help table in the image even though nothing reads it at runtime. */
static const char help[] __attribute__((used)) =
    "\nASSAY_DOC_ONLY      : documented, never getenv\n"
    "ASSAY_BOTH      : getenv and documented\n"
    "Consider setting $ASSAY_DOLLAR to x\n";

int main(void) {
    getenv("ASSAY_GETENV_ONLY");
    getenv("ASSAY_BOTH");
    return 0;
}
