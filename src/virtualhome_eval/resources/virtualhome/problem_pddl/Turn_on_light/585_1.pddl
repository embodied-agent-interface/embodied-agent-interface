(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom dining_room floor_lamp light - object
)
    (:init
    (plugged_in light)
    (has_switch floor_lamp)
    (clean light)
    (plugged_out floor_lamp)
    (has_switch light)
    (has_plug light)
    (obj_next_to light light)
    (obj_next_to light floor_lamp)
    (inside character bathroom)
    (off light)
    (off floor_lamp)
    (inside_room light bathroom)
    (movable floor_lamp)
    (inside_room light dining_room)
    (obj_next_to floor_lamp light)
    (clean floor_lamp)
)
    (:goal
    (and
        (on light)
        (plugged_in light)
        (on light)
        (plugged_in light)
        (on light)
        (plugged_in light)
    )
)
    )
    