(define (problem clearing_the_table_after_dinner)
    (:domain igibson)
    (:objects agent_n_01_1 - agent bowl_n_01_1 bowl_n_01_2 bowl_n_01_4 - bowl_n_01 bucket_n_01_1 bucket_n_01_2 - bucket_n_01 catsup_n_01_1 - catsup_n_01 floor_n_01_1 - floor_n_01 table_n_02_1 - table_n_02)
    (:init (onfloor bucket_n_01_1 floor_n_01_1) (onfloor bucket_n_01_2 floor_n_01_1) (ontop bowl_n_01_1 table_n_02_1) (ontop bowl_n_01_2 table_n_02_1) (ontop bowl_n_01_4 table_n_02_1) (ontop catsup_n_01_1 table_n_02_1) (same_obj bowl_n_01_1 bowl_n_01_1) (same_obj bowl_n_01_2 bowl_n_01_2) (same_obj bowl_n_01_4 bowl_n_01_4) (same_obj bucket_n_01_1 bucket_n_01_1) (same_obj bucket_n_01_2 bucket_n_01_2) (same_obj catsup_n_01_1 catsup_n_01_1) (same_obj floor_n_01_1 floor_n_01_1) (same_obj table_n_02_1 table_n_02_1))
    (:goal (and (inside bowl_n_01_4 bucket_n_01_1) (inside bowl_n_01_1 bucket_n_01_2) (inside catsup_n_01_1 bucket_n_01_2) (inside bowl_n_01_2 bucket_n_01_1)))
)