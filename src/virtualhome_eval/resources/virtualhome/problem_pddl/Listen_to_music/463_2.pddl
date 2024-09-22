(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office stereo - object
)
    (:init
    (inside_room stereo bedroom)
    (plugged_in stereo)
    (has_plug stereo)
    (has_switch stereo)
    (grabbable stereo)
    (off stereo)
    (movable stereo)
    (closed stereo)
    (inside character home_office)
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
    