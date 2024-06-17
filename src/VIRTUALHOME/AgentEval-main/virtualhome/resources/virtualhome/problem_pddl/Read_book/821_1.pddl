(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom novel home_office chair - object
)
    (:init
    (sittable chair)
    (movable novel)
    (surfaces chair)
    (cuttable novel)
    (obj_inside novel home_office)
    (inside character bathroom)
    (has_paper novel)
    (grabbable chair)
    (movable chair)
    (obj_inside chair home_office)
    (grabbable novel)
    (readable novel)
    (obj_next_to chair novel)
    (can_open novel)
    (obj_next_to novel chair)
)
    (:goal
    (and
        (holds_rh character novel)
    )
)
    )
    