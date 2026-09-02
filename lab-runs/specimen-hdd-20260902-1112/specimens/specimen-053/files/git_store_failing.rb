# Reduced excerpt of failing with_git_configured (not a full checkout).
# gitconfig path is unique; credential store path is not.

git_config_global_path = File.expand_path("#{SecureRandom.hex(16)}.gitconfig", tmp)
# credential helper file:
#   #{Dir.pwd}/git.store

run_shell_command(
  "git config --global credential.helper "   "'!#{credential_helper_path} --file #{Dir.pwd}/git.store'"
)
