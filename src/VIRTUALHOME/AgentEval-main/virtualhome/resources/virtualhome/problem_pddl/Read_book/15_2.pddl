(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom home_office address_book - object
)
    (:init
    (can_open address_book)
    (grabbable address_book)
    (readable address_book)
    (inside character bathroom)
    (has_paper address_book)
    (cuttable address_book)
    (obj_inside address_book home_office)
    (movable address_book)
)
    (:goal
    (and
        (holds_rh character address_book)
    )
)
    )
    