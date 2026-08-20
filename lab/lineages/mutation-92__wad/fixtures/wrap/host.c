#include <stdlib.h>

/* Help table stays LATENT. Wrapper hops must promote the getenv'd names. */
static const char help[] __attribute__((used)) =
    "\nLASH_DOC_ONLY      : documented, never getenv\n"
    "LASH_WRAP_BOTH      : wrapper getenv and documented\n"
    "Consider setting $LASH_DOLLAR to x\n";

static char *wrap_dup(void *a, void *b, void *c, const char *name)
    __attribute__((noinline));
static char *wrap_dup(void *a, void *b, void *c, const char *name) {
    (void)a;
    (void)b;
    (void)c;
    return getenv(name);
}

/* CPython _env_to_dict: getenv(&key[4]) so ENV_LASH_OFFSET → LASH_OFFSET. */
static char *env_to(const char *key) __attribute__((noinline));
static char *env_to(const char *key) {
    return getenv(key + 4);
}

int main(void) {
    wrap_dup(0, 0, 0, "LASH_WRAP_ARG3");
    wrap_dup(0, 0, 0, "LASH_WRAP_BOTH");
    env_to("ENV_LASH_OFFSET");
    getenv("LASH_DIRECT");
    return 0;
}
