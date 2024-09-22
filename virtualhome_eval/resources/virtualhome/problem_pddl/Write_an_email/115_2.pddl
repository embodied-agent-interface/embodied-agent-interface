(define (problem Write_an_email)
    (:domain virtualhome)
    (:objects
    character - character
    keyboard computer home_office bathroom chair - object
)
    (:init
    (clean computer)
    (off computer)
    (grabbable chair)
    (movable chair)
    (sittable chair)
    (surfaces chair)
    (grabbable keyboard)
    (has_plug keyboard)
    (movable keyboard)
    (has_switch computer)
    (lookable computer)
    (inside character bathroom)
    (plugged_out computer)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    