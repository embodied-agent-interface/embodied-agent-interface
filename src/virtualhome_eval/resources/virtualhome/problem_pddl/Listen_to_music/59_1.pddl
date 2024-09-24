(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    home_office phone dining_room headset - object
)
    (:init
    (obj_inside phone home_office)
    (inside_room phone dining_room)
    (grabbable headset)
    (obj_next_to headset phone)
    (grabbable phone)
    (has_plug phone)
    (movable headset)
    (obj_next_to phone headset)
    (has_switch phone)
    (inside character dining_room)
    (clothes headset)
    (obj_inside headset home_office)
    (movable phone)
)
    (:goal
    (and
        (on_char headset character)
    )
)
    )
    