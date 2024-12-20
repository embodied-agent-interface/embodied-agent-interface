(define (problem vacuuming_floors)
    (:domain igibson)
    (:objects agent_n_01_1 - agent ashcan_n_01_1 - ashcan_n_01 floor_n_01_1 - floor_n_01 vacuum_n_04_1 - vacuum_n_04)
    (:init (dusty floor_n_01_1) (onfloor agent_n_01_1 floor_n_01_1) (onfloor ashcan_n_01_1 floor_n_01_1) (onfloor vacuum_n_04_1 floor_n_01_1) (same_obj agent_n_01_1 agent_n_01_1) (same_obj ashcan_n_01_1 ashcan_n_01_1) (same_obj floor_n_01_1 floor_n_01_1) (same_obj vacuum_n_04_1 vacuum_n_04_1))
    (:goal (not (dusty floor_n_01_1)))
)