(define (problem Wash_teeth)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom toothbrush_holder bedroom tooth_paste toothbrush - object
)
    (:init
    (containers toothbrush_holder)
    (grabbable toothbrush_holder)
    (obj_next_to toothbrush toothbrush_holder)
    (movable toothbrush_holder)
    (cream tooth_paste)
    (pourable tooth_paste)
    (inside_room tooth_paste bathroom)
    (obj_next_to toothbrush_holder toothbrush)
    (inside_room toothbrush_holder bathroom)
    (movable toothbrush)
    (grabbable toothbrush)
    (obj_next_to tooth_paste toothbrush_holder)
    (inside_room toothbrush bathroom)
    (obj_ontop tooth_paste toothbrush_holder)
    (obj_next_to toothbrush_holder tooth_paste)
    (inside character bedroom)
    (grabbable tooth_paste)
    (movable tooth_paste)
    (recipient toothbrush)
    (can_open tooth_paste)
)
    (:goal
    (and
        (holds_lh character toothbrush)
    )
)
    )
    