(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom bedroom light - object
)
    (:init
    (plugged_in light)
    (clean light)
    (has_switch light)
    (has_plug light)
    (obj_next_to light light)
    (inside_room light bedroom)
    (inside character bathroom)
    (off light)
    (inside_room light bathroom)
)
    (:goal
    (and
        (on light)
        (plugged_in light)
    )
)
    )
    