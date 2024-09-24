(define (problem filling_a_Christmas_stocking)
    (:domain igibson)
    (:objects agent_n_01_1 - agent cabinet_n_01_1 - cabinet_n_01 candy_n_01_4 - candy_n_01 cube_n_05_1 cube_n_05_3 - cube_n_05 floor_n_01_1 - floor_n_01 pen_n_01_2 - pen_n_01 stocking_n_01_1 stocking_n_01_2 stocking_n_01_4 - stocking_n_01)
    (:init (inside candy_n_01_4 cabinet_n_01_1) (inside pen_n_01_2 cabinet_n_01_1) (onfloor cube_n_05_1 floor_n_01_1) (onfloor cube_n_05_3 floor_n_01_1) (onfloor stocking_n_01_1 floor_n_01_1) (onfloor stocking_n_01_2 floor_n_01_1) (onfloor stocking_n_01_4 floor_n_01_1) (same_obj cabinet_n_01_1 cabinet_n_01_1) (same_obj candy_n_01_4 candy_n_01_4) (same_obj cube_n_05_1 cube_n_05_1) (same_obj cube_n_05_3 cube_n_05_3) (same_obj floor_n_01_1 floor_n_01_1) (same_obj pen_n_01_2 pen_n_01_2) (same_obj stocking_n_01_1 stocking_n_01_1) (same_obj stocking_n_01_2 stocking_n_01_2) (same_obj stocking_n_01_4 stocking_n_01_4))
    (:goal (and (inside pen_n_01_2 stocking_n_01_2) (inside candy_n_01_4 stocking_n_01_4) (inside cube_n_05_3 stocking_n_01_4) (inside cube_n_05_1 stocking_n_01_1)))
)