(define (problem Write_an_email)
    (:domain virtualhome)
    (:objects
    character - character
    keyboard computer address_book home_office bathroom chair - object
)
    (:init
    (clean computer)
    (off computer)
    (grabbable chair)
    (movable chair)
    (sittable chair)
    (surfaces chair)
    (grabbable keyboard)
    (has_plug keyboard)
    (movable keyboard)
    (has_switch computer)
    (lookable computer)
    (can_open address_book)
    (cuttable address_book)
    (grabbable address_book)
    (has_paper address_book)
    (movable address_book)
    (readable address_book)
    (inside character bathroom)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    