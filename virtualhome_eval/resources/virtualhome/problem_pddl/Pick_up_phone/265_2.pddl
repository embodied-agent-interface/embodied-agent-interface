(define (problem Pick_up_phone)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom phone home_office button - object
)
    (:init
    (obj_inside phone home_office)
    (movable button)
    (grabbable phone)
    (inside character bathroom)
    (has_plug phone)
    (has_switch phone)
    (obj_next_to button phone)
    (obj_inside button home_office)
    (obj_next_to phone button)
    (grabbable button)
    (movable phone)
)
    (:goal
    (and
        (holds_rh character phone)
    )
)
    )
    