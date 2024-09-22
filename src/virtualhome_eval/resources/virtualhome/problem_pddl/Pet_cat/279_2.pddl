(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom cat home_office - object
)
    (:init
    (movable cat)
    (grabbable cat)
    (obj_inside cat home_office)
    (inside character bathroom)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    