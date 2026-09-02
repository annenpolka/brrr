// Reduced excerpt of compiler configuration on failing_ref
// src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
// Processor names and processorpath files are separate from compile classpath.

        compilerConfiguration.setSourceLocations( compileSourceRoots );

        compilerConfiguration.setAnnotationProcessors( annotationProcessors );

        compilerConfiguration.setProcessorPathEntries( resolveProcessorPathEntries() );

        compilerConfiguration.setSourceEncoding( encoding );
