
        let canonical = canonicalize_executable(&absolute).map_err(handle_io_error)?;

        let cache_entry = cache.entry(
            CacheBucket::Interpreter,
            cache_digest(&(
                ARCH,
                uv_platform::OsType::from_env()
                    .map(|os_type| os_type.to_string())
                    .unwrap_or_default(),
                uv_platform::OsRelease::from_env()
                    .map(|os_release| os_release.to_string())
                    .unwrap_or_default(),
            )),
            // We use the absolute path for the cache entry to avoid cache collisions for relative
            // paths. ... We include the canonical path in the cache entry as well ...
            format!("{}.msgpack", cache_digest(&(&absolute, &canonical))),
        );
