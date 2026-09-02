// Reduced excerpt of injected resolver on failing_ref
// src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
// org.apache.maven.repository.RepositorySystem is maven-compat (Maven 2 API).

    /**
     * Resolves the artifacts needed.
     */
    @Component
    private RepositorySystem repositorySystem;
