(define (problem moving_boxes_to_storage)
    (:domain igibson)
    (:objects agent_n_01_1 - agent carton_n_02_1 carton_n_02_2 - carton_n_02 floor_n_01_1 floor_n_01_2 - floor_n_01)
    (:init (onfloor agent_n_01_1 floor_n_01_2) (onfloor carton_n_02_1 floor_n_01_1) (onfloor carton_n_02_2 floor_n_01_1) (same_obj agent_n_01_1 agent_n_01_1) (same_obj carton_n_02_1 carton_n_02_1) (same_obj carton_n_02_2 carton_n_02_2) (same_obj floor_n_01_1 floor_n_01_1) (same_obj floor_n_01_2 floor_n_01_2))
    (:goal (and (ontop carton_n_02_2 carton_n_02_1) (onfloor carton_n_02_1 floor_n_01_2)))
)