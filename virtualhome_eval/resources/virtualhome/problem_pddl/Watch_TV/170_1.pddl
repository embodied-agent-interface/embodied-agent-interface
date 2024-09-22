(define (problem Watch_TV)
    (:domain virtualhome)
    (:objects
    character - character
    couch television - object
)
    (:init
    (lieable couch)
    (has_plug television)
    (has_switch television)
    (plugged_in television)
    (off television)
    (obj_next_to couch television)
    (clean television)
    (surfaces couch)
    (lookable television)
    (obj_next_to television couch)
    (movable couch)
    (facing couch television)
    (sittable couch)
)
    (:goal
    (and
        (on television)
        (plugged_in television)
        (facing character television)
    )
)
    )
    