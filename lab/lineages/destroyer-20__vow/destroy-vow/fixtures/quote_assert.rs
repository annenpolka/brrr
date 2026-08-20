#[test]
fn quotes() {
    assert_eq!(shell_single_quote("/Users/John Doe/kizu"), "'/Users/John Doe/kizu'");
    assert_eq!(cwd, Path::new("/home/user/project"));
}
