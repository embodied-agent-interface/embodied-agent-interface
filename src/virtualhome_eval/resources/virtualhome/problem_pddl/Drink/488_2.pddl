(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    cup water sink bedroom dining_room - object
)
    (:init
    (recipient sink)
    (inside_room sink dining_room)
    (containers sink)
    (inside_room water dining_room)
    (obj_ontop water sink)
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
    