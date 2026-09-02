// Reduced excerpt of Interpreter.handleCache on failing_ref
// earthfile2llb/interpreter.go
// 6b297d587cc12bea0372ca333fef34b522388b34
// Directory and mode are expanded. opts.ID is not.

func (i *Interpreter) handleCache(ctx context.Context, cmd spec.Command) error {
	opts := commandflag.CacheOpts{}
	args, err := flagutil.ParseArgsCleaned("CACHE", &opts, flagutil.GetArgsCopy(cmd))
	dir, err := i.expandArgs(ctx, args[0], false, false)
	expandedMode, err := i.expandArgs(ctx, opts.Mode, false, false)
	opts.Mode = expandedMode
	if !path.IsAbs(dir) {
		dir = path.Clean(path.Join("/", i.converter.mts.Final.MainImage.Config.WorkingDir, dir))
	}
	if err := i.converter.Cache(ctx, dir, opts); err != nil {
		return i.wrapError(err, cmd.SourceLocation, "apply CACHE")
	}
	return nil
}
