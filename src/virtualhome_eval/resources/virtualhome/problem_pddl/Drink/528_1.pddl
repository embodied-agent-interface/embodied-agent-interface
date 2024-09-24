(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    home_office freezer water dining_room drinking_glass - object
)
    (:init
    (obj_next_to freezer water)
    (inside_room water dining_room)
    (inside_room freezer dining_room)
    (obj_inside drinking_glass freezer)
    (grabbable drinking_glass)
    (closed freezer)
    (plugged_in freezer)
    (clean freezer)
    (has_switch freezer)
    (obj_next_to freezer drinking_glass)
    (pourable water)
    (pourable drinking_glass)
    (obj_next_to water freezer)
    (can_open freezer)
    (containers freezer)
    (drinkable water)
    (movable drinking_glass)
    (recipient drinking_glass)
    (has_plug freezer)
    (obj_next_to drinking_glass freezer)
    (inside character home_office)
    (inside_room drinking_glass dining_room)
)
    (:goal
    (and
        (holds_rh character drinking_glass)
    )
)
    )
    