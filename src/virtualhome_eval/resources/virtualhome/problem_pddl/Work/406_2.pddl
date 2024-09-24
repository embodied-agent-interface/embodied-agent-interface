(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    keyboard chair computer - object
)
    (:init
    (surfaces chair)
    (obj_next_to chair keyboard)
    (obj_next_to keyboard computer)
    (plugged_out computer)
    (obj_next_to computer keyboard)
    (has_plug keyboard)
    (facing chair computer)
    (movable chair)
    (obj_next_to computer chair)
    (sittable chair)
    (has_switch computer)
    (obj_next_to keyboard chair)
    (grabbable keyboard)
    (grabbable chair)
    (lookable computer)
    (clean computer)
    (off computer)
    (movable keyboard)
    (obj_next_to chair computer)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    