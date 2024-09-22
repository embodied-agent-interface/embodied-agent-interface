(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    home_office water_glass water cupboard dining_room - object
)
    (:init
    (containers cupboard)
    (obj_next_to cupboard water_glass)
    (can_open cupboard)
    (inside_room water dining_room)
    (obj_inside water cupboard)
    (inside_room cupboard dining_room)
    (closed cupboard)
    (movable water_glass)
    (pourable water_glass)
    (recipient water_glass)
    (grabbable water_glass)
    (inside_room water_glass dining_room)
    (drinkable water)
    (inside character home_office)
    (obj_inside water_glass cupboard)
    (clean cupboard)
    (obj_next_to water_glass cupboard)
    (pourable water)
)
    (:goal
    (and
        (holds_rh character water_glass)
    )
)
    )
    