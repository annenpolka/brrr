def pytest_load_initial_conftests(early_config, parser, args):
    # reporter wants --capture=sys forced from a hook
    if not any(a == "--capture=sys" or a.startswith("--capture=") or a == "-s" for a in args):
        args.append("--capture=sys")
