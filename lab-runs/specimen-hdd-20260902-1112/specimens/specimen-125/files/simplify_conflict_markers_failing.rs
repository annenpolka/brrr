// Reduced excerpt of simplify_conflict_markers on failing_ref
// crates/uv-resolver/src/graph_ops.rs
// 2bda549bcca67f06df602901ad9cdf30d35add00
// Ambiguous same-name edges are not skipped.
// Extras inferences can simplify a conflict marker to true.

    for edge_index in (0..graph.edge_count()).map(EdgeIndex::new) {
        let (from_index, _) = graph.edge_endpoints(edge_index).unwrap();
        let Some(inference_sets) = inferences.get(&from_index) else {
            continue;
        };
        let all_paths_satisfied = inference_sets.iter().all(|set| {
            graph[edge_index].conflict().evaluate(&extras, &groups)
        });
        if !all_paths_satisfied {
            continue;
        }
        for set in inference_sets {
            for inf in set {
                if inf.included {
                    graph[edge_index].assume_conflict_item(&inf.item);
                } else {
                    graph[edge_index].assume_not_conflict_item(&inf.item);
                }
            }
        }
    }
