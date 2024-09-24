(define (problem Pick_up_phone)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office phone - object
)
    (:init
    (obj_inside phone home_office)
    (plugged_in phone)
    (grabbable phone)
    (clean phone)
    (inside character bedroom)
    (has_plug phone)
    (has_switch phone)
    (off phone)
    (movable phone)
)
    (:goal
    (and
        (holds_rh character phone)
    )
)
    )
    