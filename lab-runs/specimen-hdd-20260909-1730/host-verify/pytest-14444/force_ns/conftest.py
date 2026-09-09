def pytest_load_initial_conftests(early_config, parser, args):
    args.append("--capture=sys")
    ns = getattr(early_config, "known_args_namespace", None)
    if ns is not None and hasattr(ns, "capture"):
        ns.capture = "sys"
