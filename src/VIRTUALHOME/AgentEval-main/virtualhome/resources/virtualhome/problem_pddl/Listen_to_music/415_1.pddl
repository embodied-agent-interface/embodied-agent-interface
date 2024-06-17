(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    phone headset - object
)
    (:init
    (grabbable headset)
    (grabbable phone)
    (has_plug phone)
    (movable headset)
    (has_switch phone)
    (clothes headset)
    (movable phone)
)
    (:goal
    (and
        (on_char headset character)
    )
)
    )
    