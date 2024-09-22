(define (problem Pick_up_phone)
    (:domain virtualhome)
    (:objects
    character - character
    home_office phone dining_room hair - object
)
    (:init
    (obj_inside phone home_office)
    (movable hair)
    (inside_room phone dining_room)
    (grabbable phone)
    (grabbable hair)
    (has_plug phone)
    (has_switch phone)
    (inside character dining_room)
    (body_part hair)
    (cuttable hair)
    (movable phone)
)
    (:goal
    (and
        (holds_rh character phone)
    )
)
    )
    