(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    freezer bathroom dining_room water_glass - object
)
    (:init
    (has_plug freezer)
    (obj_inside water_glass freezer)
    (can_open freezer)
    (obj_next_to freezer water_glass)
    (inside character bathroom)
    (movable water_glass)
    (pourable water_glass)
    (recipient water_glass)
    (grabbable water_glass)
    (inside_room water_glass dining_room)
    (obj_next_to water_glass freezer)
    (inside_room freezer dining_room)
    (closed freezer)
    (plugged_in freezer)
    (clean freezer)
    (has_switch freezer)
    (containers freezer)
)
    (:goal
    (and
        (holds_rh character water_glass)
    )
)
    )
    