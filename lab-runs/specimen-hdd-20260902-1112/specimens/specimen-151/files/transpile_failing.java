// Reduced excerpt of Transpilation.version cache key on failing_ref
// eo-maven-plugin/src/main/java/org/eolang/maven/Transpilation.java
// 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
// version() folds locations()/coverage/superclass. steps() omitted.
// leftover previous no-step-files result after -Deo.trackSteps=true.

String version() {
    return String.format(
        "%s-%s-%b-%b-%s",
        this.version,
        new Fingerprint(
            Stream.concat(
                Arrays.stream(Transpilation.XSLS), Arrays.stream(Transpilation.IMPORTS)
            ).toArray(String[]::new)
        ).get(),
        this.tracking.locations(), this.coverage, this.superclass
    );
}
