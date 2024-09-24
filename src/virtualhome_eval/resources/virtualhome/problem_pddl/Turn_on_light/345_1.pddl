(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    filing_cabinet home_office remote_control light dining_room - object
)
    (:init
    (grabbable remote_control)
    (has_switch light)
    (has_plug light)
    (obj_inside filing_cabinet home_office)
    (movable remote_control)
    (plugged_in light)
    (can_open filing_cabinet)
    (obj_next_to filing_cabinet light)
    (obj_next_to light light)
    (obj_next_to light filing_cabinet)
    (obj_inside remote_control home_office)
    (has_switch remote_control)
    (containers filing_cabinet)
    (clean light)
    (obj_next_to remote_control filing_cabinet)
    (inside character dining_room)
    (obj_next_to filing_cabinet remote_control)
    (surfaces filing_cabinet)
    (off light)
    (obj_ontop remote_control filing_cabinet)
    (inside_room light dining_room)
    (obj_inside light home_office)
)
    (:goal
    (and
        (on light)
        (plugged_in light)
    )
)
    )
    