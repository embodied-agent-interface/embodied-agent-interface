(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom light home_office - object
)
    (:init
    (plugged_in light)
    (clean light)
    (has_switch light)
    (has_plug light)
    (obj_next_to light light)
    (inside character bathroom)
    (off light)
    (inside_room light bathroom)
    (obj_inside light home_office)
)
    (:goal
    (and
        (on light)
        (plugged_in light)
    )
)
    )
    