(define (problem Brush_teeth)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom home_office tooth_paste toothbrush - object
)
    (:init
    (obj_next_to tooth_paste toothbrush)
    (obj_next_to toothbrush tooth_paste)
    (inside_room toothbrush bathroom)
    (inside character home_office)
    (movable tooth_paste)
    (grabbable tooth_paste)
    (cream tooth_paste)
    (pourable tooth_paste)
    (movable toothbrush)
    (can_open tooth_paste)
    (recipient toothbrush)
    (inside_room tooth_paste bathroom)
    (grabbable toothbrush)
)
    (:goal
    (and
        (holds_lh character toothbrush)
        (holds_rh character tooth_paste)
    )
)
    )
    