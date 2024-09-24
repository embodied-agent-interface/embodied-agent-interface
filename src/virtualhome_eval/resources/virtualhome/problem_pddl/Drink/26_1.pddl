(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    faucet couch hair cup television - object
)
    (:init
    (has_plug television)
    (surfaces couch)
    (recipient cup)
    (movable cup)
    (body_part hair)
    (grabbable cup)
    (lieable couch)
    (movable hair)
    (obj_next_to couch television)
    (lookable television)
    (obj_next_to faucet cup)
    (obj_next_to cup faucet)
    (movable couch)
    (cuttable hair)
    (has_switch faucet)
    (facing couch television)
    (sittable couch)
    (has_switch television)
    (grabbable hair)
    (obj_next_to television couch)
    (pourable cup)
)
    (:goal
    (and
        (holds_rh character cup)
    )
)
    )
    