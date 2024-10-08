(define (problem cleaning_microwave_oven)
    (:domain igibson)
    (:objects agent_n_01_1 - agent countertop_n_01_1 - countertop_n_01 microwave_n_02_1 - microwave_n_02 rag_n_01_1 - rag_n_01 sink_n_01_1 - sink_n_01)
    (:init (dusty microwave_n_02_1) (ontop rag_n_01_1 countertop_n_01_1) (same_obj countertop_n_01_1 countertop_n_01_1) (same_obj microwave_n_02_1 microwave_n_02_1) (same_obj rag_n_01_1 rag_n_01_1) (same_obj sink_n_01_1 sink_n_01_1) (stained microwave_n_02_1))
    (:goal (and (not (dusty microwave_n_02_1)) (not (stained microwave_n_02_1))))
)