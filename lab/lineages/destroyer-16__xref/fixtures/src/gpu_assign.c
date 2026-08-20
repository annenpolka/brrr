#include <stdio.h>
/* GPU assembler NAME = table. STACK_SIZE is ENV_SUFFIXES. */
static const char table[] __attribute__((used)) =
    "SQ_PGM_RESOURCES:STACK_SIZE =\0"
    "SOME_CONST = \0"
    "AMDGPU_BUFFER_ATOMIC_ADD      : opcode\n";
int main(void) {
    puts(table);
    return 0;
}
