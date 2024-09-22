(define (problem filling_an_Easter_basket)
    (:domain igibson)
    (:objects agent_n_01_1 - agent basket_n_01_1 basket_n_01_2 - basket_n_01 bow_n_08_2 - bow_n_08 cabinet_n_01_2 - cabinet_n_01 candy_n_01_1 candy_n_01_2 - candy_n_01 countertop_n_01_1 - countertop_n_01 egg_n_02_1 - egg_n_02 electric_refrigerator_n_01_1 - electric_refrigerator_n_01)
    (:init (cooked egg_n_02_1) (inside bow_n_08_2 cabinet_n_01_2) (inside egg_n_02_1 electric_refrigerator_n_01_1) (ontop basket_n_01_1 countertop_n_01_1) (ontop basket_n_01_2 countertop_n_01_1) (ontop candy_n_01_1 electric_refrigerator_n_01_1) (ontop candy_n_01_2 electric_refrigerator_n_01_1) (same_obj basket_n_01_1 basket_n_01_1) (same_obj basket_n_01_2 basket_n_01_2) (same_obj bow_n_08_2 bow_n_08_2) (same_obj cabinet_n_01_2 cabinet_n_01_2) (same_obj candy_n_01_1 candy_n_01_1) (same_obj candy_n_01_2 candy_n_01_2) (same_obj countertop_n_01_1 countertop_n_01_1) (same_obj egg_n_02_1 egg_n_02_1) (same_obj electric_refrigerator_n_01_1 electric_refrigerator_n_01_1))
    (:goal (and (inside egg_n_02_1 basket_n_01_1) (inside candy_n_01_2 basket_n_01_1) (ontop bow_n_08_2 basket_n_01_1) (inside candy_n_01_1 basket_n_01_2)))
)