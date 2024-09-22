(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    mouse keyboard computer - object
)
    (:init
    (off computer)
    (obj_next_to mouse keyboard)
    (obj_next_to computer mouse)
    (has_plug mouse)
    (has_switch computer)
    (obj_next_to computer keyboard)
    (obj_next_to keyboard mouse)
    (grabbable keyboard)
    (movable mouse)
    (obj_next_to mouse computer)
    (obj_next_to keyboard computer)
    (plugged_out computer)
    (grabbable mouse)
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
    