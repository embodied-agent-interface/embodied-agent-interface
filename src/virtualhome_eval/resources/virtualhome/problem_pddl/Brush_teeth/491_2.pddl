(define (problem Brush_teeth)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom dining_room tooth_paste toothbrush - object
)
    (:init
    (inside_room toothbrush bathroom)
    (inside character dining_room)
    (recipient toothbrush)
    (cream tooth_paste)
    (movable toothbrush)
    (grabbable tooth_paste)
    (movable tooth_paste)
    (can_open tooth_paste)
    (pourable tooth_paste)
    (inside_room tooth_paste bathroom)
    (grabbable toothbrush)
)
    (:goal
    (and
        (holds_lh character tooth_paste)
        (holds_rh character toothbrush)
    )
)
    )
    