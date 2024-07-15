(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    home_office dining_room water drinking_glass - object
)
    (:init
    (inside_room water dining_room)
    (pourable drinking_glass)
    (drinkable water)
    (grabbable drinking_glass)
    (inside character home_office)
    (movable drinking_glass)
    (obj_next_to drinking_glass water)
    (obj_next_to water drinking_glass)
    (inside_room drinking_glass dining_room)
    (pourable water)
    (recipient drinking_glass)
)
    (:goal
    (and
        (holds_rh character drinking_glass)
    )
)
    )
    