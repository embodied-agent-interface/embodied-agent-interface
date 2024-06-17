(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom home_office water_glass couch water television dining_room - object
)
    (:init
    (has_plug television)
    (inside_room water dining_room)
    (surfaces couch)
    (inside_room television dining_room)
    (obj_inside couch home_office)
    (pourable water)
    (lieable couch)
    (obj_next_to couch television)
    (movable water_glass)
    (pourable water_glass)
    (lookable television)
    (inside_room water_glass dining_room)
    (obj_next_to water water_glass)
    (obj_next_to water_glass water)
    (drinkable water)
    (movable couch)
    (facing couch television)
    (sittable couch)
    (has_switch television)
    (inside character bathroom)
    (recipient water_glass)
    (grabbable water_glass)
    (obj_inside television home_office)
    (obj_next_to television couch)
)
    (:goal
    (and
        (holds_rh character water_glass)
    )
)
    )
    