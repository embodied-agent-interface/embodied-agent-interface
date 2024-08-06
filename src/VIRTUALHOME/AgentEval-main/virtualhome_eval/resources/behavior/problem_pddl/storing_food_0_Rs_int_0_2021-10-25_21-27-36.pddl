(define (problem storing_food)
    (:domain igibson)
    (:objects agent_n_01_1 - agent cabinet_n_01_1 - cabinet_n_01 chip_n_04_2 - chip_n_04 countertop_n_01_1 - countertop_n_01 sugar_n_01_1 sugar_n_01_2 - sugar_n_01 vegetable_oil_n_01_2 - vegetable_oil_n_01)
    (:init (ontop chip_n_04_2 countertop_n_01_1) (ontop sugar_n_01_1 countertop_n_01_1) (ontop sugar_n_01_2 countertop_n_01_1) (ontop vegetable_oil_n_01_2 countertop_n_01_1) (same_obj cabinet_n_01_1 cabinet_n_01_1) (same_obj chip_n_04_2 chip_n_04_2) (same_obj countertop_n_01_1 countertop_n_01_1) (same_obj sugar_n_01_1 sugar_n_01_1) (same_obj sugar_n_01_2 sugar_n_01_2) (same_obj vegetable_oil_n_01_2 vegetable_oil_n_01_2))
    (:goal (and (inside vegetable_oil_n_01_2 cabinet_n_01_1) (inside sugar_n_01_1 cabinet_n_01_1) (inside chip_n_04_2 cabinet_n_01_1) (inside sugar_n_01_2 cabinet_n_01_1)))
)