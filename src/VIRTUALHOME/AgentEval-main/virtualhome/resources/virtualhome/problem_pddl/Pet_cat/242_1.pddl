(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    home_office cat dining_room - object
)
    (:init
    (movable cat)
    (grabbable cat)
    (obj_inside cat home_office)
    (inside character dining_room)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    