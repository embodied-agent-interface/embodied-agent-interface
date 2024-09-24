(define (problem cleaning_garage)
    (:domain igibson)
    (:objects agent_n_01_1 - agent bin_n_01_1 - bin_n_01 bottle_n_01_1 - bottle_n_01 cabinet_n_01_1 - cabinet_n_01 floor_n_01_1 - floor_n_01 newspaper_n_03_2 - newspaper_n_03 rag_n_01_1 - rag_n_01 sink_n_01_1 - sink_n_01 table_n_02_1 - table_n_02)
    (:init (dusty cabinet_n_01_1) (onfloor bin_n_01_1 floor_n_01_1) (onfloor bottle_n_01_1 floor_n_01_1) (onfloor newspaper_n_03_2 floor_n_01_1) (ontop rag_n_01_1 table_n_02_1) (same_obj bin_n_01_1 bin_n_01_1) (same_obj bottle_n_01_1 bottle_n_01_1) (same_obj cabinet_n_01_1 cabinet_n_01_1) (same_obj floor_n_01_1 floor_n_01_1) (same_obj newspaper_n_03_2 newspaper_n_03_2) (same_obj rag_n_01_1 rag_n_01_1) (same_obj sink_n_01_1 sink_n_01_1) (same_obj table_n_02_1 table_n_02_1))
    (:goal (and (inside newspaper_n_03_2 bin_n_01_1) (not (dusty cabinet_n_01_1)) (not (stained cabinet_n_01_1)) (ontop bottle_n_01_1 table_n_02_1)))
)