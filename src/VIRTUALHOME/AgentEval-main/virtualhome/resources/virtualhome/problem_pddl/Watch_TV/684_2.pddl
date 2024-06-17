(define (problem Watch_TV)
    (:domain virtualhome)
    (:objects
    character - character
    home_office remote_control dining_room television - object
)
    (:init
    (grabbable remote_control)
    (obj_next_to remote_control television)
    (has_switch television)
    (has_plug television)
    (plugged_in television)
    (off television)
    (clean television)
    (obj_next_to television remote_control)
    (inside_room television dining_room)
    (lookable television)
    (obj_inside television home_office)
    (inside character dining_room)
    (obj_inside remote_control home_office)
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
    