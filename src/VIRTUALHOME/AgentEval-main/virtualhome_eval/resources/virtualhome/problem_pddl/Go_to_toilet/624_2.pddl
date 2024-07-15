(define (problem Go_to_toilet)
    (:domain virtualhome)
    (:objects
    character - character
    toilet toilet_paper dresser - object
)
    (:init
    (cuttable toilet_paper)
    (can_open toilet)
    (grabbable toilet_paper)
    (obj_next_to toilet dresser)
    (obj_next_to toilet_paper toilet)
    (obj_next_to dresser dresser)
    (can_open dresser)
    (sittable toilet)
    (containers toilet)
    (hangable toilet_paper)
    (movable toilet_paper)
    (obj_next_to dresser toilet)
    (obj_next_to toilet toilet_paper)
    (containers dresser)
    (cover_object toilet_paper)
    (has_paper toilet_paper)
)
    (:goal
    (and
        (ontop character toilet)
    )
)
    )
    