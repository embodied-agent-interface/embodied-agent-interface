(define (problem polishing_silver)
    (:domain igibson)
    (:objects agent_n_01_1 - agent cabinet_n_01_1 - cabinet_n_01 rag_n_01_1 - rag_n_01 spoon_n_01_1 spoon_n_01_2 spoon_n_01_3 spoon_n_01_4 - spoon_n_01)
    (:init (dusty spoon_n_01_1) (dusty spoon_n_01_3) (dusty spoon_n_01_4) (inside rag_n_01_1 cabinet_n_01_1) (inside spoon_n_01_1 cabinet_n_01_1) (inside spoon_n_01_2 cabinet_n_01_1) (inside spoon_n_01_3 cabinet_n_01_1) (inside spoon_n_01_4 cabinet_n_01_1) (same_obj cabinet_n_01_1 cabinet_n_01_1) (same_obj rag_n_01_1 rag_n_01_1) (same_obj spoon_n_01_1 spoon_n_01_1) (same_obj spoon_n_01_2 spoon_n_01_2) (same_obj spoon_n_01_3 spoon_n_01_3) (same_obj spoon_n_01_4 spoon_n_01_4))
    (:goal (and (inside spoon_n_01_4 cabinet_n_01_1) (not (dusty spoon_n_01_3)) (inside spoon_n_01_3 cabinet_n_01_1) (not (dusty spoon_n_01_1))))
)