(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    water_glass bedroom dining_room - object
)
    (:init
    (inside character bedroom)
    (pourable water_glass)
    (inside_room water_glass dining_room)
    (recipient water_glass)
    (grabbable water_glass)
    (movable water_glass)
)
    (:goal
    (and
        (holds_rh character water_glass)
    )
)
    )
    