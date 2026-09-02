// Reduced excerpt of ConfigurableFileCollectionCodec on failing_ref
// 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
// Named collection contents are stored. Resolver / base directory is not.

    override suspend fun WriteContext.encode(value: ConfigurableFileCollection) {
        require(value is DefaultConfigurableFileCollection)
        encodePreservingIdentityOf(value) {
            codec.run {
                encodeContents(value)
            }
            writeBoolean(value.isFinalizing)
        }
    }

    override suspend fun ReadContext.decode(): ConfigurableFileCollection {
        return decodePreservingIdentity { id ->
            val contents = codec.run { decodeContents() }
            val fileCollection = fileCollectionFactory.configurableFiles()
            fileCollection.from(contents)
            if (readBoolean()) {
                fileCollection.finalizeValue()
            }
            isolate.identities.putInstance(id, fileCollection)
            fileCollection
        }
    }
