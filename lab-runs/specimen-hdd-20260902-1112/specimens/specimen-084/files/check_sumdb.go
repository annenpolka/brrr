# Reduced excerpt of cmd/go checkSumDB (consumer of Client.Lookup)
# golang/go src/cmd/go/internal/modfetch/fetch.go
# on vendor parent ef97884827ab7f4ec41b0b21c9d40f80092936ab
# lookupSumDB -> sumdb.Client.Lookup lines are the sumdb identity.

	db, lines, err := lookupSumDB(mod)
	if err != nil {
		return module.VersionError(modWithoutSuffix, fmt.Errorf("verifying %s: %v", noun, err))
	}

	have := mod.Path + " " + mod.Version + " " + h
	prefix := mod.Path + " " + mod.Version + " h1:"
	for _, line := range lines {
		if line == have {
			return nil
		}
		if strings.HasPrefix(line, prefix) {
			return module.VersionError(modWithoutSuffix, fmt.Errorf("verifying %s: checksum mismatch\n\tdownloaded: %v\n\t%s: %v"+sumdbMismatch, noun, h, db, line[len(prefix)-len("h1:"):]))
		}
	}
	return module.VersionError(modWithoutSuffix, fmt.Errorf("verifying %s: checksum missing from sumdb response"+sumdbAbsent, noun))
