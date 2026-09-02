// Reduced excerpt on failing_ref
// src/git-command-manager.ts

async tryConfigUnsetValue(
  configKey: string,
  configValue: string,
  globalConfig?: boolean,
  configFile?: string
): Promise<boolean> {
  const args = ['config']
  if (configFile) {
    args.push('--file', configFile)
  } else {
    args.push(globalConfig ? '--global' : '--local')
  }
  args.push('--unset', configKey, configValue)
  const output = await this.execGit(args, true)
  return output.exitCode === 0
}
