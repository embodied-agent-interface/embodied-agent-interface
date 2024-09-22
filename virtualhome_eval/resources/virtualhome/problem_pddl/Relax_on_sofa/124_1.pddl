(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    home_office hair couch bedroom television - object
)
    (:init
    (lieable couch)
    (has_plug television)
    (has_switch television)
    (movable hair)
    (obj_next_to couch television)
    (grabbable hair)
    (obj_inside hair home_office)
    (surfaces couch)
    (inside character bedroom)
    (lookable television)
    (obj_inside television home_office)
    (movable couch)
    (body_part hair)
    (cuttable hair)
    (obj_inside couch home_office)
    (facing couch television)
    (obj_next_to television couch)
    (sittable couch)
)
    (:goal
    (and
        (sitting character)
        (ontop character couch)
    )
)
    )
    