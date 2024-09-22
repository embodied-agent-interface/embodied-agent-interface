(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    couch novel - object
)
    (:init
    (obj_next_to couch novel)
    (lieable couch)
    (movable novel)
    (cuttable novel)
    (surfaces couch)
    (has_paper novel)
    (movable couch)
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
    