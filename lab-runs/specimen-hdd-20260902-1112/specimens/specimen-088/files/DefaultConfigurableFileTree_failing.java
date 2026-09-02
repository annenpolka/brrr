# Reduced excerpt of DefaultConfigurableFileTree on failing_ref
# 040aac7031d900c2c548154fcbc75627b01e386c
# subprojects/file-collections/src/main/java/org/gradle/api/internal/file/collections/DefaultConfigurableFileTree.java
# No getFiles / isEmpty / contains / visit override.

public class DefaultConfigurableFileTree extends CompositeFileTree implements ConfigurableFileTree {
    private Object dir;
    private final PatternSet patternSet;
    private final PathToFileResolver resolver;
    private final DefaultTaskDependency buildDependency;
    private final DirectoryFileTreeFactory directoryFileTreeFactory;

    public DefaultConfigurableFileTree(PathToFileResolver resolver, Factory<PatternSet> patternSetFactory, TaskDependencyFactory taskDependencyFactory, DirectoryFileTreeFactory directoryFileTreeFactory) {
        super(taskDependencyFactory);
        this.resolver = resolver;
        this.directoryFileTreeFactory = directoryFileTreeFactory;
        patternSet = patternSetFactory.create();
        buildDependency = taskDependencyFactory.configurableDependency();
    }

    @Override
    protected void visitChildren(Consumer<FileCollectionInternal> visitor) {
        File dir = getDir();
        visitor.accept(new FileTreeAdapter(directoryFileTreeFactory.create(dir, patternSet), taskDependencyFactory, patternSetFactory));
    }
}
