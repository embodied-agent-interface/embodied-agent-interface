(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom home_office mouse button computer - object
)
    (:init
    (off computer)
    (movable button)
    (obj_next_to computer mouse)
    (has_plug mouse)
    (has_switch computer)
    (obj_inside mouse home_office)
    (obj_inside computer home_office)
    (inside character bathroom)
    (movable mouse)
    (obj_next_to mouse computer)
    (plugged_out computer)
    (grabbable mouse)
    (obj_inside button home_office)
    (obj_next_to button computer)
    (lookable computer)
    (obj_next_to computer button)
    (clean computer)
    (grabbable button)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    