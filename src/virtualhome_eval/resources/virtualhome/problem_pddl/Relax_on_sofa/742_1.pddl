(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    home_office couch dining_room television - object
)
    (:init
    (lieable couch)
    (has_plug television)
    (has_switch television)
    (obj_next_to couch television)
    (surfaces couch)
    (inside_room television dining_room)
    (lookable television)
    (obj_inside television home_office)
    (movable couch)
    (obj_inside couch home_office)
    (obj_next_to television couch)
    (inside character dining_room)
    (facing couch television)
    (sittable couch)
)
    (:goal
    (and
        (sitting character)
        (ontop character couch)
    )
)
    )
    