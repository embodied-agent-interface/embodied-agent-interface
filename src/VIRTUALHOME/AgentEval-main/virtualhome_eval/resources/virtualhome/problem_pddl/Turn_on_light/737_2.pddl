(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    home_office dining_room light - object
)
    (:init
    (plugged_in light)
    (clean light)
    (has_switch light)
    (has_plug light)
    (obj_next_to light light)
    (off light)
    (inside character dining_room)
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
    