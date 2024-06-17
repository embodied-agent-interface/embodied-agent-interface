(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    novel - object
)
    (:init
    (movable novel)
    (cuttable novel)
    (has_paper novel)
    (grabbable novel)
    (readable novel)
    (can_open novel)
)
    (:goal
    (and
        (holds_rh character novel)
    )
)
    )
    