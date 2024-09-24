(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom dining_room cup water - object
)
    (:init
    (inside_room water dining_room)
    (recipient cup)
    (inside character bedroom)
    (movable cup)
    (drinkable water)
    (inside_room cup dining_room)
    (pourable cup)
    (pourable water)
    (grabbable cup)
)
    (:goal
    (and
        (holds_rh character cup)
    )
)
    )
    