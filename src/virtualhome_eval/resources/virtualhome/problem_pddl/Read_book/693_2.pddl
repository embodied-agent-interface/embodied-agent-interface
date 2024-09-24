(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom bedroom chair novel - object
)
    (:init
    (sittable chair)
    (movable novel)
    (surfaces chair)
    (cuttable novel)
    (inside_room chair bedroom)
    (inside character bathroom)
    (has_paper novel)
    (grabbable chair)
    (movable chair)
    (inside_room novel bedroom)
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
    