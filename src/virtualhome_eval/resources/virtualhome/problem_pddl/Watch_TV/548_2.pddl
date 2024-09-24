(define (problem Watch_TV)
    (:domain virtualhome)
    (:objects
    character - character
    remote_control television - object
)
    (:init
    (grabbable remote_control)
    (has_switch television)
    (has_plug television)
    (plugged_in television)
    (off television)
    (clean television)
    (lookable television)
    (has_switch remote_control)
    (movable remote_control)
)
    (:goal
    (and
        (on television)
        (plugged_in television)
        (facing character television)
    )
)
    )
    