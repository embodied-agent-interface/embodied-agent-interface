(define (problem preparing_salad)
    (:domain igibson)
    (:objects agent_n_01_1 - agent apple_n_01_1 apple_n_01_2 - apple_n_01 cabinet_n_01_1 - cabinet_n_01 carving_knife_n_01_1 - carving_knife_n_01 countertop_n_01_1 - countertop_n_01 electric_refrigerator_n_01_1 - electric_refrigerator_n_01 lettuce_n_03_1 lettuce_n_03_2 - lettuce_n_03 plate_n_04_2 - plate_n_04 radish_n_01_1 radish_n_01_2 - radish_n_01 tomato_n_01_2 - tomato_n_01)
    (:init (inside carving_knife_n_01_1 cabinet_n_01_1) (inside plate_n_04_2 cabinet_n_01_1) (inside tomato_n_01_2 electric_refrigerator_n_01_1) (not (dusty plate_n_04_2)) (ontop apple_n_01_1 countertop_n_01_1) (ontop apple_n_01_2 countertop_n_01_1) (ontop lettuce_n_03_1 countertop_n_01_1) (ontop lettuce_n_03_2 countertop_n_01_1) (ontop radish_n_01_1 countertop_n_01_1) (ontop radish_n_01_2 countertop_n_01_1) (same_obj apple_n_01_1 apple_n_01_1) (same_obj apple_n_01_2 apple_n_01_2) (same_obj cabinet_n_01_1 cabinet_n_01_1) (same_obj carving_knife_n_01_1 carving_knife_n_01_1) (same_obj countertop_n_01_1 countertop_n_01_1) (same_obj electric_refrigerator_n_01_1 electric_refrigerator_n_01_1) (same_obj lettuce_n_03_1 lettuce_n_03_1) (same_obj lettuce_n_03_2 lettuce_n_03_2) (same_obj plate_n_04_2 plate_n_04_2) (same_obj radish_n_01_1 radish_n_01_1) (same_obj radish_n_01_2 radish_n_01_2) (same_obj tomato_n_01_2 tomato_n_01_2))
    (:goal (and (sliced apple_n_01_1) (ontop tomato_n_01_2 plate_n_04_2) (ontop lettuce_n_03_1 plate_n_04_2) (sliced apple_n_01_2)))
)