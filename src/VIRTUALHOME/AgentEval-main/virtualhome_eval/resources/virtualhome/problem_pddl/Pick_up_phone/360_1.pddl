(define (problem Pick_up_phone)
    (:domain virtualhome)
    (:objects
    character - character
    home_office phone dining_room - object
)
    (:init
    (obj_inside phone home_office)
    (inside_room phone dining_room)
    (grabbable phone)
    (has_plug phone)
    (has_switch phone)
    (inside character dining_room)
    (movable phone)
)
    (:goal
    (and
        (holds_rh character phone)
    )
)
    )
    