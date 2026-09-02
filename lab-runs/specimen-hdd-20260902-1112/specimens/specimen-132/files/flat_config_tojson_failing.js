// Reduced excerpt of FlatConfigArray toJSON on failing_ref
// lib/config/flat-config-array.js
// b3634f695ddab6a82c0a9b1d8695e62b60d23366
// Plugins serialized as namespaces only. Plugin name@version omitted.

                return {
                    ...this,
                    plugins: Object.keys(plugins),
                    languageOptions: {
                        ...languageOptions,
                        parser: parserName
                    },
                    processor: processorName
                };
