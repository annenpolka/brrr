#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Owed and never consulted. Keep the token in the image under -O. */
static const char k_idle[] __attribute__((used)) = "LATENT_DUE_IDLE";

int main(void)
{
    char synth[16];
    const char *used;
    const char *built;

    memcpy(synth, "LATENT_", 7);
    memcpy(synth + 7, "SYNTH", 5);
    synth[12] = '\0';

    used = getenv("LATENT_DUE_USED");
    built = getenv(synth);
    printf("probe-ok used=%s synth=%s idle=%c\n",
           used ? "y" : "n", built ? "y" : "n", k_idle[0]);
    return 0;
}
