(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom couch home_office television - object
)
    (:init
    (lieable couch)
    (has_plug television)
    (has_switch television)
    (obj_next_to couch television)
    (surfaces couch)
    (inside character bathroom)
    (lookable television)
    (obj_inside television home_office)
    (movable couch)
    (obj_inside couch home_office)
    (obj_next_to television couch)
    (facing couch television)
    (sittable couch)
)
    (:goal
    (and
        (lying character)
        (ontop character couch)
    )
)
    )
    