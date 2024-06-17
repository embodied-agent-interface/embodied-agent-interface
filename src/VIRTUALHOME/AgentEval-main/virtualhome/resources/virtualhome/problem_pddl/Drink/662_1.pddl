(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    water_glass bedroom dining_room water - object
)
    (:init
    (inside_room water dining_room)
    (inside character bedroom)
    (pourable water_glass)
    (movable water_glass)
    (recipient water_glass)
    (grabbable water_glass)
    (inside_room water_glass dining_room)
    (drinkable water)
    (pourable water)
)
    (:goal
    (and
        (holds_rh character water_glass)
    )
)
    )
    