// Reduced excerpt of GitInputScheme::getDefaultRef on failing_ref
// src/libfetchers/git.cc

auto head = std::visit(
    overloaded{
        [&](const std::filesystem::path & path) { return GitRepo::openRepo(path, {})->getWorkdirRef(); },
        [&](const ParsedURL & url) { return readHeadCached(settings, url.to_string(), shallow); }},
    repoInfo.location);
if (!head) {
    warn("could not read HEAD ref from repo at '%s', using 'master'", repoInfo.locationToArg());
    return "master";
}
return *head;
