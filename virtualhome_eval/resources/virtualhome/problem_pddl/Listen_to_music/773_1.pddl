(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    stereo - object
)
    (:init
    (plugged_in stereo)
    (has_plug stereo)
    (has_switch stereo)
    (grabbable stereo)
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
    