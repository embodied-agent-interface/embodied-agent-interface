(define (problem chopping_vegetables)
    (:domain igibson)
    (:objects agent_n_01_1 - agent cabinet_n_01_1 - cabinet_n_01 chestnut_n_03_1 chestnut_n_03_2 - chestnut_n_03 countertop_n_01_1 - countertop_n_01 dish_n_01_2 - dish_n_01 electric_refrigerator_n_01_1 - electric_refrigerator_n_01 knife_n_01_1 - knife_n_01 mushroom_n_05_1 mushroom_n_05_2 - mushroom_n_05 tomato_n_01_1 tomato_n_01_2 - tomato_n_01 vidalia_onion_n_01_2 - vidalia_onion_n_01)
    (:init (inside dish_n_01_2 cabinet_n_01_1) (inside vidalia_onion_n_01_2 electric_refrigerator_n_01_1) (ontop chestnut_n_03_1 countertop_n_01_1) (ontop chestnut_n_03_2 countertop_n_01_1) (ontop knife_n_01_1 countertop_n_01_1) (ontop mushroom_n_05_1 countertop_n_01_1) (ontop mushroom_n_05_2 countertop_n_01_1) (ontop tomato_n_01_1 countertop_n_01_1) (ontop tomato_n_01_2 countertop_n_01_1) (same_obj cabinet_n_01_1 cabinet_n_01_1) (same_obj chestnut_n_03_1 chestnut_n_03_1) (same_obj chestnut_n_03_2 chestnut_n_03_2) (same_obj countertop_n_01_1 countertop_n_01_1) (same_obj dish_n_01_2 dish_n_01_2) (same_obj electric_refrigerator_n_01_1 electric_refrigerator_n_01_1) (same_obj knife_n_01_1 knife_n_01_1) (same_obj mushroom_n_05_1 mushroom_n_05_1) (same_obj mushroom_n_05_2 mushroom_n_05_2) (same_obj tomato_n_01_1 tomato_n_01_1) (same_obj tomato_n_01_2 tomato_n_01_2) (same_obj vidalia_onion_n_01_2 vidalia_onion_n_01_2))
    (:goal (and (sliced vidalia_onion_n_01_2) (inside chestnut_n_03_1 dish_n_01_2) (sliced tomato_n_01_1) (sliced mushroom_n_05_1)))
)