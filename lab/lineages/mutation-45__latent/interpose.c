/*
 * latent getenv interposer.
 *
 * macOS: DYLD_INSERT_LIBRARIES + GOT rebind (DYLD_INTERPOSE of getenv
 * segfaults during dyld bootstrap; a constructor + fishhook-style patch
 * is what actually works).
 * Linux: LD_PRELOAD + dlsym(RTLD_NEXT).
 *
 * Logs one name per line to $LATENT_LOG. First line is "#loaded" so the
 * parent can tell insert survived SIP / hardened-runtime stripping.
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static char *(*orig_getenv)(const char *) = NULL;
static int logfd = -1;
static int ready = 0;
static __thread int in_hook = 0;

static void log_name(const char *name)
{
    size_t n;
    if (!ready || logfd < 0 || !name || !name[0])
        return;
    if (strcmp(name, "LATENT_LOG") == 0)
        return;
    n = 0;
    while (name[n] && n < 200)
        n++;
    (void)!write(logfd, name, n);
    (void)!write(logfd, "\n", 1);
}

static char *sys_getenv(const char *name)
{
    return orig_getenv ? orig_getenv(name) : NULL;
}

char *latent_getenv(const char *name)
{
    char *out;
    if (in_hook)
        return sys_getenv(name);
    in_hook = 1;
    if (ready)
        log_name(name);
    out = sys_getenv(name);
    in_hook = 0;
    return out;
}

#ifdef __APPLE__
#include <dlfcn.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <mach-o/nlist.h>
#include <mach/mach.h>
#include <stdint.h>

#ifdef __LP64__
typedef struct mach_header_64 mach_header_t;
typedef struct segment_command_64 segment_command_t;
typedef struct section_64 section_t;
typedef struct nlist_64 nlist_t;
#define LC_SEGMENT_ARCH LC_SEGMENT_64
#else
typedef struct mach_header mach_header_t;
typedef struct segment_command segment_command_t;
typedef struct section section_t;
typedef struct nlist nlist_t;
#define LC_SEGMENT_ARCH LC_SEGMENT
#endif

static int name_is_getenv(const char *name)
{
    if (name[0] == '_')
        name++;
    /* _getenv$DARWIN_EXTSN and friends */
    if (strncmp(name, "getenv", 6) != 0)
        return 0;
    return name[6] == '\0' || name[6] == '$';
}

static void rebind_section(section_t *sect, intptr_t slide, nlist_t *symtab,
                           char *strtab, uint32_t *indirect)
{
    uint32_t *indices;
    void **bindings;
    uint32_t count, k;
    long ps;
    vm_address_t page, mask;
    vm_size_t sz;

    indices = indirect + sect->reserved1;
    bindings = (void **)((uintptr_t)slide + sect->addr);
    count = (uint32_t)(sect->size / sizeof(void *));
    if (count == 0)
        return;

    ps = sysconf(_SC_PAGESIZE);
    if (ps <= 0)
        ps = 4096;
    mask = (vm_address_t)ps - 1;
    page = (vm_address_t)bindings & ~mask;
    sz = (vm_size_t)sect->size + ((vm_address_t)bindings & mask);
    (void)vm_protect(mach_task_self(), page, sz, 0,
                     VM_PROT_READ | VM_PROT_WRITE | VM_PROT_COPY);

    for (k = 0; k < count; k++) {
        uint32_t symIndex = indices[k];
        uint32_t strx;
        const char *nm;
        if (symIndex == INDIRECT_SYMBOL_ABS ||
            symIndex == INDIRECT_SYMBOL_LOCAL ||
            symIndex == (INDIRECT_SYMBOL_LOCAL | INDIRECT_SYMBOL_ABS))
            continue;
        strx = symtab[symIndex].n_un.n_strx;
        nm = strtab + strx;
        if (name_is_getenv(nm))
            bindings[k] = (void *)latent_getenv;
    }
}

static void rebind_image(const struct mach_header *header, intptr_t slide)
{
    segment_command_t *linkedit = NULL;
    struct symtab_command *symtab_cmd = NULL;
    struct dysymtab_command *dysymtab_cmd = NULL;
    uintptr_t cur = (uintptr_t)header + sizeof(mach_header_t);
    uint32_t ncmds = ((const mach_header_t *)header)->ncmds;
    uint32_t i;
    nlist_t *symtab;
    char *strtab;
    uint32_t *indirect;
    uintptr_t linkedit_base;

    for (i = 0; i < ncmds; i++) {
        segment_command_t *cmd = (segment_command_t *)cur;
        if (cmd->cmd == LC_SEGMENT_ARCH) {
            if (strcmp(cmd->segname, SEG_LINKEDIT) == 0)
                linkedit = cmd;
        } else if (cmd->cmd == LC_SYMTAB) {
            symtab_cmd = (struct symtab_command *)cmd;
        } else if (cmd->cmd == LC_DYSYMTAB) {
            dysymtab_cmd = (struct dysymtab_command *)cmd;
        }
        cur += cmd->cmdsize;
    }
    if (!linkedit || !symtab_cmd || !dysymtab_cmd)
        return;

    linkedit_base = (uintptr_t)slide + linkedit->vmaddr - linkedit->fileoff;
    symtab = (nlist_t *)(linkedit_base + symtab_cmd->symoff);
    strtab = (char *)(linkedit_base + symtab_cmd->stroff);
    indirect = (uint32_t *)(linkedit_base + dysymtab_cmd->indirectsymoff);

    cur = (uintptr_t)header + sizeof(mach_header_t);
    for (i = 0; i < ncmds; i++) {
        segment_command_t *cmd = (segment_command_t *)cur;
        if (cmd->cmd == LC_SEGMENT_ARCH &&
            (strcmp(cmd->segname, SEG_DATA) == 0 ||
             strcmp(cmd->segname, "__DATA_CONST") == 0 ||
             strcmp(cmd->segname, "__AUTH_CONST") == 0)) {
            section_t *sect = (section_t *)(cur + sizeof(segment_command_t));
            uint32_t j;
            for (j = 0; j < cmd->nsects; j++) {
                uint32_t type = sect[j].flags & SECTION_TYPE;
                if (type == S_LAZY_SYMBOL_POINTERS ||
                    type == S_NON_LAZY_SYMBOL_POINTERS)
                    rebind_section(&sect[j], slide, symtab, strtab, indirect);
            }
        }
        cur += cmd->cmdsize;
    }
}

static int skip_rebind(const char *fname)
{
    /* Rebinding libSystem's getenv GOT makes orig_getenv recurse. */
    if (!fname)
        return 1;
    if (strstr(fname, "liblatent"))
        return 1;
    if (strstr(fname, "/libSystem"))
        return 1;
    if (strstr(fname, "/libsystem_"))
        return 1;
    if (strstr(fname, "/usr/lib/system/"))
        return 1;
    if (strstr(fname, "/usr/lib/libc"))
        return 1;
    if (strstr(fname, "/usr/lib/libobjc"))
        return 1;
    if (strstr(fname, "/usr/lib/libc++"))
        return 1;
    if (strstr(fname, "/usr/lib/dyld"))
        return 1;
    return 0;
}

static void add_image(const struct mach_header *mh, intptr_t slide)
{
    Dl_info info;
    memset(&info, 0, sizeof(info));
    if (dladdr(mh, &info) && skip_rebind(info.dli_fname))
        return;
    rebind_image(mh, slide);
}

static void init(void) __attribute__((constructor));
static void init(void)
{
    const char *p;
    orig_getenv = getenv; /* still the real one */
    p = orig_getenv ? orig_getenv("LATENT_LOG") : NULL;
    if (p && p[0])
        logfd = open(p, O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (logfd >= 0) {
        const char msg[] = "#loaded\n";
        (void)!write(logfd, msg, sizeof(msg) - 1);
    }
    ready = 1;
    _dyld_register_func_for_add_image(add_image);
}

#else /* Linux / ELF */

#include <dlfcn.h>

static char *(*orig_secure_getenv)(const char *) = NULL;

static void init(void) __attribute__((constructor));
static void init(void)
{
    const char *p;
    orig_getenv = (char *(*)(const char *))dlsym(RTLD_NEXT, "getenv");
    orig_secure_getenv =
        (char *(*)(const char *))dlsym(RTLD_NEXT, "secure_getenv");
    p = orig_getenv ? orig_getenv("LATENT_LOG") : NULL;
    if (p && p[0])
        logfd = open(p, O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (logfd >= 0) {
        const char msg[] = "#loaded\n";
        (void)!write(logfd, msg, sizeof(msg) - 1);
    }
    ready = 1;
}

char *getenv(const char *name)
{
    return latent_getenv(name);
}

char *secure_getenv(const char *name)
{
    if (ready)
        log_name(name);
    if (orig_secure_getenv)
        return orig_secure_getenv(name);
    return sys_getenv(name);
}

#endif
