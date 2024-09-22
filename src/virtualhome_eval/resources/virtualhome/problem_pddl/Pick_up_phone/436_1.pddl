(define (problem Pick_up_phone)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom phone home_office - object
)
    (:init
    (obj_inside phone home_office)
    (grabbable phone)
    (inside character bathroom)
    (has_plug phone)
    (has_switch phone)
    (movable phone)
)
    (:goal
    (and
        (holds_rh character phone)
    )
)
    )
    