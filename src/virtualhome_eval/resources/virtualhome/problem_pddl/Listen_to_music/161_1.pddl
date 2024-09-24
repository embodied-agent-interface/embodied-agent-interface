(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    home_office dining_room stereo - object
)
    (:init
    (plugged_in stereo)
    (obj_inside stereo home_office)
    (has_plug stereo)
    (has_switch stereo)
    (grabbable stereo)
    (off stereo)
    (movable stereo)
    (closed stereo)
    (inside character dining_room)
    (surfaces stereo)
    (clean stereo)
    (can_open stereo)
)
    (:goal
    (and
        (closed stereo)
        (on stereo)
        (plugged_in stereo)
    )
)
    )
    