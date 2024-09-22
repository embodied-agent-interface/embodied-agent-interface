(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom computer home_office - object
)
    (:init
    (off computer)
    (has_switch computer)
    (obj_inside computer home_office)
    (inside character bathroom)
    (plugged_out computer)
    (lookable computer)
    (clean computer)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    