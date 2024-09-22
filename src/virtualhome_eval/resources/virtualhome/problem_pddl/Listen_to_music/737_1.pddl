(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office stereo - object
)
    (:init
    (plugged_in stereo)
    (obj_inside stereo home_office)
    (has_plug stereo)
    (has_switch stereo)
    (grabbable stereo)
    (inside character bedroom)
    (off stereo)
    (movable stereo)
    (closed stereo)
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
    