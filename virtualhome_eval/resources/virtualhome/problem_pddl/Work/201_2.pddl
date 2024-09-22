(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office keyboard computer - object
)
    (:init
    (off computer)
    (has_switch computer)
    (obj_next_to computer keyboard)
    (obj_inside computer home_office)
    (inside character bedroom)
    (grabbable keyboard)
    (obj_next_to keyboard computer)
    (inside_room keyboard bedroom)
    (plugged_out computer)
    (obj_inside keyboard home_office)
    (inside_room computer bedroom)
    (movable keyboard)
    (lookable computer)
    (has_plug keyboard)
    (clean computer)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    