(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office cat - object
)
    (:init
    (movable cat)
    (grabbable cat)
    (obj_inside cat home_office)
    (inside character bedroom)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    