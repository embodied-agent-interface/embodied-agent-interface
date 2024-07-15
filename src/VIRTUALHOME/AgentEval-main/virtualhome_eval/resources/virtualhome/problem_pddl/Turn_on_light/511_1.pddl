(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    light - object
)
    (:init
    (plugged_in light)
    (clean light)
    (has_switch light)
    (has_plug light)
    (obj_next_to light light)
    (off light)
)
    (:goal
    (and
        (on light)
        (plugged_in light)
    )
)
    )
    