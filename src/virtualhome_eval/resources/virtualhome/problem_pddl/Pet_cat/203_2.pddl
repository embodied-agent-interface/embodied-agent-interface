(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom cat home_office hair - object
)
    (:init
    (grabbable cat)
    (obj_inside cat home_office)
    (movable hair)
    (grabbable hair)
    (inside character bathroom)
    (body_part hair)
    (cuttable hair)
    (movable cat)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    