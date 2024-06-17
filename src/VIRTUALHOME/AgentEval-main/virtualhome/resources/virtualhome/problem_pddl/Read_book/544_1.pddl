(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office novel - object
)
    (:init
    (movable novel)
    (cuttable novel)
    (has_paper novel)
    (inside_room novel bedroom)
    (inside character home_office)
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
    