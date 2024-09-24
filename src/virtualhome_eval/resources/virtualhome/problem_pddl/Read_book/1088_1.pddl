(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    couch filing_cabinet novel - object
)
    (:init
    (can_open filing_cabinet)
    (containers filing_cabinet)
    (surfaces filing_cabinet)
    (lieable couch)
    (movable novel)
    (obj_ontop novel filing_cabinet)
    (cuttable novel)
    (obj_next_to novel filing_cabinet)
    (surfaces couch)
    (has_paper novel)
    (movable couch)
    (obj_next_to filing_cabinet novel)
    (grabbable novel)
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
    