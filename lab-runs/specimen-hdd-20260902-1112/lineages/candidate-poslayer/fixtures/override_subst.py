#!/usr/bin/env python3
def subst(template: str, posargs: list[str]) -> str:
    return template.replace("{posargs}", " ".join(posargs))

def main() -> None:
    file_template = "pytest {posargs}"
    posargs = ["tests", "src"]
    file_cmd = subst(file_template, posargs)
    override = "pytest {posargs}"
    file_argv = file_cmd.split()
    override_argv = override.split()
    print("file_argv", file_argv)
    print("override_argv", override_argv)
    print("cli_leftover", posargs)
    print("override_exit", 0)
    print("override_ran_against", override_argv[-1])

if __name__ == "__main__":
    main()
