#include <stdlib.h>
#include <string.h>

/* Help table stays LATENT. CString hop must promote the getenv'd names. */
static const char help[] __attribute__((used)) =
    "\nWAD_DOC_ONLY      : documented, never getenv\n"
    "WAD_CSTRING_BOTH      : cstring getenv and documented\n"
    "Consider setting $WAD_DOLLAR to x\n";

/* Inlined Rust env::var: memcpy (ptr,len) onto the stack, NUL, getenv. */
static char *wad_var(const char *p, unsigned long n) __attribute__((noinline));
static char *wad_var(const char *p, unsigned long n) {
    char buf[64];
    memcpy(buf, p, n);
    buf[n] = 0;
    return getenv(buf);
}

int main(void) {
    wad_var("WAD_CSTRING", 11);
    wad_var("WAD_CSTRING_BOTH", 16);
    getenv("WAD_DIRECT");
    return 0;
}
