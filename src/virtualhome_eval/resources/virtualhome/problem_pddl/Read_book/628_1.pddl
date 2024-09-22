(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom novel home_office couch television - object
)
    (:init
    (has_plug television)
    (surfaces couch)
    (obj_inside couch home_office)
    (readable novel)
    (lieable couch)
    (obj_next_to couch television)
    (obj_inside novel home_office)
    (has_paper novel)
    (lookable television)
    (obj_next_to couch novel)
    (movable novel)
    (cuttable novel)
    (movable couch)
    (grabbable novel)
    (obj_next_to novel couch)
    (facing couch television)
    (sittable couch)
    (can_open novel)
    (has_switch television)
    (inside character bathroom)
    (obj_inside television home_office)
    (obj_next_to television couch)
)
    (:goal
    (and
        (holds_rh character novel)
    )
)
    )
    