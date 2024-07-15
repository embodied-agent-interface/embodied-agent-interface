(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office light - object
)
    (:init
    (plugged_in light)
    (clean light)
    (has_switch light)
    (has_plug light)
    (obj_next_to light light)
    (inside_room light bedroom)
    (inside character bedroom)
    (off light)
    (obj_inside light home_office)
)
    (:goal
    (and
        (on light)
        (plugged_in light)
        (on light)
        (plugged_in light)
    )
)
    )
    