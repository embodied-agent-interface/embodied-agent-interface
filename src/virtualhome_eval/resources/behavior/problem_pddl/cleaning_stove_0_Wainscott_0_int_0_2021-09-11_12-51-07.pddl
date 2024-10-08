(define (problem cleaning_stove)
    (:domain igibson)
    (:objects agent_n_01_1 - agent cabinet_n_01_1 - cabinet_n_01 dishtowel_n_01_1 - dishtowel_n_01 rag_n_01_1 - rag_n_01 sink_n_01_1 - sink_n_01 stove_n_01_1 - stove_n_01)
    (:init (dusty stove_n_01_1) (inside dishtowel_n_01_1 cabinet_n_01_1) (inside rag_n_01_1 cabinet_n_01_1) (not (soaked dishtowel_n_01_1)) (not (soaked rag_n_01_1)) (not (stained rag_n_01_1)) (same_obj cabinet_n_01_1 cabinet_n_01_1) (same_obj dishtowel_n_01_1 dishtowel_n_01_1) (same_obj rag_n_01_1 rag_n_01_1) (same_obj sink_n_01_1 sink_n_01_1) (same_obj stove_n_01_1 stove_n_01_1) (stained stove_n_01_1))
    (:goal (and (nextto rag_n_01_1 sink_n_01_1) (not (dusty stove_n_01_1)) (nextto dishtowel_n_01_1 sink_n_01_1) (not (stained stove_n_01_1))))
)