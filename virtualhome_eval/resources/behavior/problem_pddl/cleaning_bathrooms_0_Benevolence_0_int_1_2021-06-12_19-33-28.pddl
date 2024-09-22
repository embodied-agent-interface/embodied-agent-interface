(define (problem cleaning_bathrooms)
    (:domain igibson)
    (:objects agent_n_01_1 - agent bucket_n_01_1 - bucket_n_01 floor_n_01_1 - floor_n_01 rag_n_01_1 - rag_n_01 sink_n_01_1 - sink_n_01 soap_n_01_1 - soap_n_01 toilet_n_02_1 - toilet_n_02)
    (:init (inside soap_n_01_1 sink_n_01_1) (not (soaked rag_n_01_1)) (onfloor agent_n_01_1 floor_n_01_1) (onfloor bucket_n_01_1 floor_n_01_1) (onfloor rag_n_01_1 floor_n_01_1) (same_obj agent_n_01_1 agent_n_01_1) (same_obj bucket_n_01_1 bucket_n_01_1) (same_obj floor_n_01_1 floor_n_01_1) (same_obj rag_n_01_1 rag_n_01_1) (same_obj sink_n_01_1 sink_n_01_1) (same_obj soap_n_01_1 soap_n_01_1) (same_obj toilet_n_02_1 toilet_n_02_1) (stained floor_n_01_1) (stained sink_n_01_1) (stained toilet_n_02_1))
    (:goal (and (not (stained toilet_n_02_1)) (not (stained floor_n_01_1)) (inside rag_n_01_1 bucket_n_01_1) (not (stained sink_n_01_1))))
)