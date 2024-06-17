(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    hair bedroom dining_room stereo - object
)
    (:init
    (inside_room stereo bedroom)
    (plugged_in stereo)
    (movable hair)
    (grabbable hair)
    (has_plug stereo)
    (has_switch stereo)
    (grabbable stereo)
    (off stereo)
    (cuttable hair)
    (movable stereo)
    (closed stereo)
    (inside character dining_room)
    (body_part hair)
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
    