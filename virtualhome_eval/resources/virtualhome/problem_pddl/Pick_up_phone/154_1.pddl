(define (problem Pick_up_phone)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom dining_room phone button - object
)
    (:init
    (movable button)
    (inside_room phone dining_room)
    (grabbable phone)
    (has_plug phone)
    (has_switch phone)
    (inside_room phone bedroom)
    (obj_next_to button phone)
    (inside character dining_room)
    (obj_next_to phone button)
    (inside_room button bedroom)
    (grabbable button)
    (movable phone)
)
    (:goal
    (and
        (holds_rh character phone)
    )
)
    )
    