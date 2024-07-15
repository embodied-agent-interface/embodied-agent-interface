(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    couch television - object
)
    (:init
    (lieable couch)
    (has_plug television)
    (has_switch television)
    (obj_next_to couch television)
    (surfaces couch)
    (lookable television)
    (obj_next_to television couch)
    (movable couch)
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
    