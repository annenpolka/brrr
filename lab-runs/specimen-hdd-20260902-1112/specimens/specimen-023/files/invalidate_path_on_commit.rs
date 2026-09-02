
    // Create a Git repository (regular .git directory, loose ref).
    context
        .temp_dir
        .child(".git")
        .child("HEAD")
        .write_str("ref: refs/heads/main")?;
    context
        .temp_dir
        .child(".git")
        .child("refs")
        .child("heads")
        .child("main")
        .write_str("1b6638fdb424e993d8354e75c55a3e524050c857")?;

    // uv pip install -r requirements.txt  -> prepares example @ ./editable
    // second install -> "Checked 1 package"
    // change refs/heads/main to another 40-hex
    // third install -> re-prepares example
