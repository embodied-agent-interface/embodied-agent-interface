(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    home_office cat hair couch bedroom television - object
)
    (:init
    (obj_next_to cat couch)
    (has_plug television)
    (surfaces couch)
    (body_part hair)
    (obj_inside couch home_office)
    (grabbable cat)
    (lieable couch)
    (movable hair)
    (obj_next_to couch television)
    (lookable television)
    (obj_inside cat home_office)
    (obj_next_to couch cat)
    (movable couch)
    (cuttable hair)
    (movable cat)
    (facing couch television)
    (sittable couch)
    (has_switch television)
    (grabbable hair)
    (inside character bedroom)
    (obj_inside television home_office)
    (obj_next_to television couch)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    