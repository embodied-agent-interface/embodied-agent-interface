(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    light floor_lamp - object
)
    (:init
    (plugged_in light)
    (has_switch floor_lamp)
    (clean light)
    (plugged_out floor_lamp)
    (has_switch light)
    (has_plug light)
    (obj_next_to light light)
    (off light)
    (off floor_lamp)
    (movable floor_lamp)
    (obj_next_to floor_lamp light)
    (obj_next_to light floor_lamp)
    (clean floor_lamp)
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
    