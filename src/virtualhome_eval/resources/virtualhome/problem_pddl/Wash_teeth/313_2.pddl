(define (problem Wash_teeth)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom bathroom_counter teeth sink towel dining_room tooth_paste toothbrush - object
)
    (:init
    (obj_next_to sink toothbrush)
    (containers sink)
    (grabbable teeth)
    (inside_room sink bathroom)
    (cream tooth_paste)
    (pourable tooth_paste)
    (cover_object towel)
    (inside_room tooth_paste bathroom)
    (inside_room sink dining_room)
    (obj_next_to sink tooth_paste)
    (obj_next_to sink bathroom_counter)
    (obj_next_to sink towel)
    (movable toothbrush)
    (obj_next_to bathroom_counter sink)
    (movable teeth)
    (grabbable toothbrush)
    (obj_next_to sink teeth)
    (inside_room towel bathroom)
    (inside_room toothbrush bathroom)
    (obj_ontop tooth_paste sink)
    (obj_next_to towel sink)
    (obj_inside sink bathroom_counter)
    (inside character dining_room)
    (movable towel)
    (grabbable towel)
    (inside_room bathroom_counter bathroom)
    (inside_room teeth bathroom)
    (recipient sink)
    (obj_next_to tooth_paste sink)
    (obj_next_to teeth sink)
    (surfaces bathroom_counter)
    (obj_next_to toothbrush sink)
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
    