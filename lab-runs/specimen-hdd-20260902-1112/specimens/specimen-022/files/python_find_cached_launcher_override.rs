
fn python_find_cached_launcher_override() {
    let context = uv_test::test_context!("3.12");
    let other_venv = context.temp_dir.child("other");

    context
        .venv()
        .arg("--python")
        .arg("3.12")
        .arg(other_venv.path())
        .assert()
        .success();

    let requested_python = venv_bin_path(&other_venv).join("python3");
    let override_python = venv_bin_path(&context.venv).join("python3");

    // `PYTHONEXECUTABLE` makes the requested `other` interpreter report `.venv`.
    uv_snapshot!(context.filters(), context.python_find()
        .arg(&requested_python)
        .env("PYTHONEXECUTABLE", &override_python), @"
    exit_code: 0 (success)
    ----- stdout -----
    [VENV]/bin/python3
    ");

    // Without `PYTHONEXECUTABLE`, this should return `other`, not the cached `.venv`.
    uv_snapshot!(context.filters(), context.python_find()
        .arg(&requested_python)
        .env_remove("PYTHONEXECUTABLE"), @"
    exit_code: 0 (success)
    ----- stdout -----
    [VENV]/bin/python3
    ");
}
