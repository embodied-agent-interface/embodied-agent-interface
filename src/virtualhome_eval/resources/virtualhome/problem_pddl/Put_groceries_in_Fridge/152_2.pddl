(define (problem Put_groceries_in_Fridge)
    (:domain virtualhome)
    (:objects
    character - character
    freezer bathroom dining_room food_food - object
)
    (:init
    (has_plug freezer)
    (inside_room food_food dining_room)
    (can_open freezer)
    (grabbable food_food)
    (inside character bathroom)
    (movable food_food)
    (obj_next_to freezer food_food)
    (inside_room freezer dining_room)
    (obj_next_to food_food freezer)
    (closed freezer)
    (plugged_in freezer)
    (clean freezer)
    (eatable food_food)
    (has_switch freezer)
    (cuttable food_food)
    (containers freezer)
)
    (:goal
    (and
        (open freezer)
        (plugged_in freezer)
        (obj_inside food_food freezer)
    )
)
    )
    