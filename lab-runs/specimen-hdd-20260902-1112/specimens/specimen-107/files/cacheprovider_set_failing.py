# Reduced excerpt of Cache.set / mkdir / _ensure_supporting_files on failing_ref
# src/_pytest/cacheprovider.py
# 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
# Directory existence is the initialized-cache identity.
# Supporting files are written only when that identity is absent.

    def mkdir(self, name: str) -> Path:
        path = Path(name)
        if len(path.parts) > 1:
            raise ValueError("name is not allowed to contain path separators")
        res = self._cachedir.joinpath(self._CACHE_PREFIX_DIRS, path)
        res.mkdir(exist_ok=True, parents=True)
        return res

    def set(self, key: str, value: object) -> None:
        path = self._getvaluepath(key)
        try:
            if path.parent.is_dir():
                cache_dir_exists_already = True
            else:
                cache_dir_exists_already = self._cachedir.exists()
                path.parent.mkdir(exist_ok=True, parents=True)
        except OSError as exc:
            self.warn(
                f"could not create cache path {path}: {exc}",
                _ispytest=True,
            )
            return
        if not cache_dir_exists_already:
            self._ensure_supporting_files()
        data = json.dumps(value, ensure_ascii=False, indent=2)
        try:
            f = path.open("w", encoding="UTF-8")
        except OSError as exc:
            self.warn(
                f"cache could not write path {path}: {exc}",
                _ispytest=True,
            )
        else:
            with f:
                f.write(data)

    def _ensure_supporting_files(self) -> None:
        readme_path = self._cachedir / "README.md"
        readme_path.write_text(README_CONTENT, encoding="UTF-8")
        gitignore_path = self._cachedir.joinpath(".gitignore")
        msg = "# Created by pytest automatically.\n*\n"
        gitignore_path.write_text(msg, encoding="UTF-8")
        cachedir_tag_path = self._cachedir.joinpath("CACHEDIR.TAG")
        cachedir_tag_path.write_bytes(CACHEDIR_TAG_CONTENT)
