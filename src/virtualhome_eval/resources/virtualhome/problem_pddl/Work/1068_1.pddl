(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office computer - object
)
    (:init
    (off computer)
    (has_switch computer)
    (obj_inside computer home_office)
    (inside character bedroom)
    (plugged_out computer)
    (inside_room computer bedroom)
    (lookable computer)
    (clean computer)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    