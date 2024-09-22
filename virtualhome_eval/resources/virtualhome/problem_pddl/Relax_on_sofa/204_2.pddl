(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    home_office couch bedroom television coffee - object
)
    (:init
    (has_plug television)
    (movable coffee)
    (surfaces couch)
    (obj_inside couch home_office)
    (lieable couch)
    (obj_next_to coffee couch)
    (drinkable coffee)
    (obj_next_to couch television)
    (grabbable coffee)
    (obj_next_to television coffee)
    (lookable television)
    (pourable coffee)
    (movable couch)
    (facing couch television)
    (sittable couch)
    (has_switch television)
    (inside character bedroom)
    (obj_inside coffee home_office)
    (obj_next_to couch coffee)
    (obj_inside television home_office)
    (obj_next_to television couch)
    (obj_next_to coffee television)
)
    (:goal
    (and
        (lying character)
        (ontop character couch)
    )
)
    )
    