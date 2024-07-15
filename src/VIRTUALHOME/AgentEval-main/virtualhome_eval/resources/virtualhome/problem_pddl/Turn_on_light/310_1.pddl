(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    dining_room bedroom light - object
)
    (:init
    (plugged_in light)
    (clean light)
    (has_switch light)
    (has_plug light)
    (obj_next_to light light)
    (inside_room light bedroom)
    (off light)
    (inside character dining_room)
    (inside_room light dining_room)
)
    (:goal
    (and
        (on light)
        (plugged_in light)
    )
)
    )
    