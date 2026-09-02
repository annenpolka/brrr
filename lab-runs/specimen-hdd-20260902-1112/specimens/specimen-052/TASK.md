# TASK

A CRD embeds `PodTemplateSpec` / `PodSpec`. Regenerating the CRD OpenAPI with Kubernetes 1.30 `code-generator` / `controller-gen` adds list-map annotations on `imagePullSecrets` and `hostAliases`. Applying that CRD is rejected by the apiserver. The same CRD generated against 1.29 applied.

The developer wants to know which generated schema fields the apiserver is treating as map keys, and how those fields are marked on the handwritten Go types versus the generated OpenAPI.
