(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    home_office computer dining_room - object
)
    (:init
    (off computer)
    (has_switch computer)
    (obj_inside computer home_office)
    (plugged_out computer)
    (inside character dining_room)
    (lookable computer)
    (clean computer)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    