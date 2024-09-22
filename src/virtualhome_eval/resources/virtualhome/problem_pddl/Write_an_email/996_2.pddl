(define (problem Write_an_email)
    (:domain virtualhome)
    (:objects
    character - character
    keyboard computer dining_room bathroom chair - object
)
    (:init
    (clean computer)
    (off computer)
    (grabbable chair)
    (movable chair)
    (sittable chair)
    (surfaces chair)
    (has_switch computer)
    (lookable computer)
    (grabbable keyboard)
    (has_plug keyboard)
    (movable keyboard)
    (inside character dining_room)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    