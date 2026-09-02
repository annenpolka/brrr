// Reduced excerpt of resolveProcessorPathEntries on failing_ref
// src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
// c62de5ccc75ff404d8ab5d6aa428434c127fb161
// Extra GAVs in annotationProcessorPaths. maven-compat resolve.
// Request carries local repo + remotes only.

    private List<String> resolveProcessorPathEntries()
        throws MojoExecutionException
    {
        if ( annotationProcessorPaths == null || annotationProcessorPaths.isEmpty() )
        {
            return null;
        }

        try
        {
            Set<String> elements = new LinkedHashSet<>();
            for ( DependencyCoordinate coord : annotationProcessorPaths )
            {
                ArtifactHandler handler = artifactHandlerManager.getArtifactHandler( coord.getType() );

                Artifact artifact = new DefaultArtifact(
                     coord.getGroupId(),
                     coord.getArtifactId(),
                     VersionRange.createFromVersionSpec( coord.getVersion() ),
                     Artifact.SCOPE_RUNTIME,
                     coord.getType(),
                     coord.getClassifier(),
                     handler,
                     false );

                ArtifactResolutionRequest request = new ArtifactResolutionRequest()
                                .setArtifact( artifact )
                                .setResolveRoot( true )
                                .setResolveTransitively( true )
                                .setLocalRepository( session.getLocalRepository() )
                                .setRemoteRepositories( project.getRemoteArtifactRepositories() );

                ArtifactResolutionResult resolutionResult = repositorySystem.resolve( request );

                resolutionErrorHandler.throwErrors( request, resolutionResult );

                for ( Artifact resolved : resolutionResult.getArtifacts() )
                {
                    elements.add( resolved.getFile().getAbsolutePath() );
                }
            }
            return new ArrayList<>( elements );
        }
        catch ( Exception e )
        {
            throw new MojoExecutionException( "Resolution of annotationProcessorPath dependencies failed: "
                + e.getLocalizedMessage(), e );
        }
    }
