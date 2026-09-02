// Reduced excerpt of computeSignature / d.ts emit signature on failing_ref
// src/compiler/builder.ts
// 8ed846c73b5033087eee119ae00511e019f91729
// File signature identity is hash of d.ts emit text only.
// d.ts emit diagnostics are not part of that identity.

    export function computeSignature(text: string, data: WriteFileCallbackData | undefined, computeHash: BuilderState.ComputeHash | undefined) {
        return BuilderState.computeSignature(data?.sourceMapUrlPos !== undefined ? text.substring(0, data.sourceMapUrlPos) : text, computeHash);
    }

                if (isDeclarationFileName(fileName)) {
                    if (!outFile(state.compilerOptions)) {
                        Debug.assert(sourceFiles?.length === 1);
                        let newSignature;
                        if (!customTransformers) {
                            const file = sourceFiles[0];
                            const info = state.fileInfos.get(file.resolvedPath)!;
                            if (info.signature === file.version) {
                                newSignature = computeSignature(text, data, computeHash);
                                if (newSignature !== file.version) {
                                    info.signature = newSignature;
                                }
                            }
                        }
                    }
                }
