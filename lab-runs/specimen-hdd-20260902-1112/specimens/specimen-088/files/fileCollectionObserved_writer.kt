# Reduced excerpt of ConfigurationCacheFingerprintWriter on failing_ref
# 040aac7031d900c2c548154fcbc75627b01e386c
# implements UndeclaredBuildInputListener

override fun fileOpened(file: File, consumer: String?) {
    if (isInputTrackingDisabled() || isExecutingTask()) {
        return
    }
    captureFile(file)
    reportUniqueFileInput(file, consumer)
}

override fun fileCollectionObserved(fileCollection: FileCollection, consumer: String) {
    if (isInputTrackingDisabled()) {
        return
    }
    captureWorkInputs(consumer) { it(fileCollection as FileCollectionInternal) }
}

private inline fun captureWorkInputs(workDisplayName: String, content: ((FileCollectionInternal) -> Unit) -> Unit) {
    val fileSystemInputs = simplify(content)
    sink().write(
        ConfigurationCacheFingerprint.WorkInputs(
            workDisplayName,
            fileSystemInputs,
            host.fingerprintOf(fileSystemInputs)
        )
    )
}
