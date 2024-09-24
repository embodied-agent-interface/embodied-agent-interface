(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    home_office mouse keyboard bedroom computer - object
)
    (:init
    (obj_inside mouse home_office)
    (obj_next_to keyboard computer)
    (plugged_out computer)
    (grabbable mouse)
    (obj_next_to computer keyboard)
    (has_plug keyboard)
    (has_switch computer)
    (obj_next_to keyboard mouse)
    (grabbable keyboard)
    (obj_next_to mouse computer)
    (obj_inside keyboard home_office)
    (obj_next_to mouse keyboard)
    (has_plug mouse)
    (lookable computer)
    (clean computer)
    (inside_room mouse bedroom)
    (off computer)
    (obj_next_to computer mouse)
    (obj_inside computer home_office)
    (inside character bedroom)
    (movable mouse)
    (inside_room keyboard bedroom)
    (inside_room computer bedroom)
    (movable keyboard)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    