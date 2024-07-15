(define (problem Write_an_email)
    (:domain virtualhome)
    (:objects
    character - character
    keyboard computer dining_room home_office mouse chair - object
)
    (:init
    (clean keyboard)
    (plugged_out keyboard)
    (clean computer)
    (off computer)
    (clean mouse)
    (plugged_out mouse)
    (grabbable chair)
    (movable chair)
    (sittable chair)
    (surfaces chair)
    (grabbable mouse)
    (has_plug mouse)
    (movable mouse)
    (grabbable keyboard)
    (has_plug keyboard)
    (movable keyboard)
    (has_switch computer)
    (lookable computer)
    (inside character dining_room)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    