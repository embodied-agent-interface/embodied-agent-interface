(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom couch home_office novel - object
)
    (:init
    (obj_next_to couch novel)
    (lieable couch)
    (movable novel)
    (cuttable novel)
    (surfaces couch)
    (obj_inside novel home_office)
    (inside character bathroom)
    (has_paper novel)
    (movable couch)
    (obj_inside couch home_office)
    (grabbable novel)
    (obj_next_to novel couch)
    (readable novel)
    (sittable couch)
    (can_open novel)
)
    (:goal
    (and
        (holds_rh character novel)
    )
)
    )
    