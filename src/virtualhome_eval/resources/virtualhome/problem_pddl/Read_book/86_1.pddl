(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    filing_cabinet bathroom novel home_office - object
)
    (:init
    (can_open filing_cabinet)
    (containers filing_cabinet)
    (surfaces filing_cabinet)
    (obj_ontop novel filing_cabinet)
    (movable novel)
    (cuttable novel)
    (obj_next_to novel filing_cabinet)
    (obj_inside novel home_office)
    (inside character bathroom)
    (has_paper novel)
    (obj_next_to filing_cabinet novel)
    (grabbable novel)
    (obj_inside filing_cabinet home_office)
    (readable novel)
    (can_open novel)
)
    (:goal
    (and
        (holds_rh character novel)
    )
)
    )
    