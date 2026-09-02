// Reduced excerpt on failing_ref
// libs/javalib/src/mill/javalib/JavaModule.scala
// libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala
// e69f7bb6e18c84793c3950714a4092f4a62bf498
// compile dest is persistent. Generated .class identity is omitted from analysis.

  def zincIncrementalCompilation: T[Boolean] = Task { allSourceFiles().length > 1 }

  def compile: T[mill.javalib.api.CompilationResult] = Task(persistent = true) {
    val compileGenSources = compileGeneratedSources()
    os.remove.all(compileGenSources)   // -s dir only
    os.makeDir.all(compileGenSources)
    worker.apply(
      ZincOp.CompileJava(
        incrementalCompilation = zincIncrementalCompilation(),
        workDir = Task.dest
      ),
      ...
    )
  }

      pr = if (incrementalCompilation) {
        val prev = store.get()
        PreviousResult.of(prev.map(_.getAnalysis), prev.map(_.getMiniSetup))
      } else {
        PreviousResult.of(Optional.empty[CompileAnalysis], Optional.empty[MiniSetup])
      }

// IncrementalAnnotationProcessing does not exist on failing_ref.
