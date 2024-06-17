(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom freezer water_glass water dining_room - object
)
    (:init
    (obj_next_to freezer water)
    (inside_room water dining_room)
    (inside_room freezer dining_room)
    (has_switch freezer)
    (pourable water)
    (movable water_glass)
    (pourable water_glass)
    (inside_room water_glass dining_room)
    (obj_next_to water freezer)
    (obj_inside water freezer)
    (can_open freezer)
    (drinkable water)
    (has_plug freezer)
    (obj_next_to freezer water_glass)
    (inside character bathroom)
    (recipient water_glass)
    (grabbable water_glass)
    (obj_next_to water_glass freezer)
    (containers freezer)
)
    (:goal
    (and
        (holds_rh character water_glass)
    )
)
    )
    