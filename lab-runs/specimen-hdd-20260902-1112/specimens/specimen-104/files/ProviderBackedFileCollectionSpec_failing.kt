// Reduced excerpt of FileCollectionCodec on failing_ref
// Provider-backed named collection stores the provider only.
// Decode uses leftover isolate fileCollectionFactory (root base dir).

private
class ProviderBackedFileCollectionSpec(val provider: ProviderInternal<*>)

                    is ProviderBackedFileCollectionSpec -> element.provider

            is ProviderBackedFileCollection -> {
                val provider = fileCollection.provider
                if (provider !is TaskProvider<*>) {
                    elements.add(ProviderBackedFileCollectionSpec(provider))
                    false
                } else {
                    true
                }
            }
