(define (problem Watch_TV)
    (:domain virtualhome)
    (:objects
    character - character
    home_office remote_control electrical_outlet bedroom chair television - object
)
    (:init
    (grabbable remote_control)
    (has_plug television)
    (obj_next_to chair remote_control)
    (surfaces chair)
    (clean television)
    (obj_next_to television remote_control)
    (clean electrical_outlet)
    (obj_next_to electrical_outlet remote_control)
    (movable chair)
    (movable remote_control)
    (obj_next_to chair television)
    (obj_next_to chair electrical_outlet)
    (obj_next_to remote_control television)
    (sittable chair)
    (plugged_in television)
    (obj_inside electrical_outlet home_office)
    (obj_next_to television chair)
    (lookable television)
    (has_switch electrical_outlet)
    (obj_inside remote_control home_office)
    (has_switch remote_control)
    (obj_next_to electrical_outlet chair)
    (off television)
    (obj_next_to remote_control electrical_outlet)
    (inside_room chair bedroom)
    (grabbable chair)
    (obj_next_to remote_control chair)
    (off electrical_outlet)
    (has_switch television)
    (inside character bedroom)
    (obj_inside television home_office)
    (obj_inside chair home_office)
)
    (:goal
    (and
        (on television)
        (plugged_in television)
        (facing character television)
    )
)
    )
    