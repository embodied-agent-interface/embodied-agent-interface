(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    home_office dining_room controller light - object
)
    (:init
    (plugged_in light)
    (clean light)
    (obj_next_to light controller)
    (has_switch light)
    (has_plug light)
    (grabbable controller)
    (movable controller)
    (obj_next_to light light)
    (obj_inside controller home_office)
    (off light)
    (obj_next_to controller controller)
    (inside character dining_room)
    (inside_room light dining_room)
    (has_plug controller)
    (obj_next_to controller light)
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
    