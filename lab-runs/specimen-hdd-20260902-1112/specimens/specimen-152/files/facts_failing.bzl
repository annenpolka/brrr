# Reduced excerpt of apt facts key on failing_ref
# apt/extensions.bzl
# 42dd9a20c5c761e4131325a2cf594a753ffffa2d
# pkg_fact_key is dist/component/arch/Packages. snapshot URL omitted.
# leftover previous integrity after snapshot URL upgrade.

pkg_fact_key = dist + "/" + component + "/" + architecture + "/Packages"
cnt_fact_key = dist + "/" + component + "/" + architecture + "/Contents"
cached_pkg_format = formats.get(pkg_fact_key)
# glock.facts().get(pkg_fact_key) is the leftover integrity on HIT
