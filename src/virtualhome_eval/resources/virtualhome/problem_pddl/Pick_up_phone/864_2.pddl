(define (problem Pick_up_phone)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom phone home_office hair - object
)
    (:init
    (obj_inside phone home_office)
    (movable hair)
    (grabbable phone)
    (grabbable hair)
    (inside character bathroom)
    (has_plug phone)
    (has_switch phone)
    (body_part hair)
    (cuttable hair)
    (inside_room hair bathroom)
    (movable phone)
)
    (:goal
    (and
        (holds_rh character phone)
    )
)
    )
    