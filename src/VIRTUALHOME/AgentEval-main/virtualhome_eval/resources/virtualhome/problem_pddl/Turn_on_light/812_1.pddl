(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    dining_room bedroom light floor_lamp - object
)
    (:init
    (plugged_in light)
    (has_switch floor_lamp)
    (clean light)
    (plugged_out floor_lamp)
    (has_switch light)
    (has_plug light)
    (obj_next_to light light)
    (inside_room light bedroom)
    (inside_room floor_lamp bedroom)
    (off light)
    (off floor_lamp)
    (movable floor_lamp)
    (inside character dining_room)
    (inside_room light dining_room)
    (obj_next_to floor_lamp light)
    (obj_next_to light floor_lamp)
    (clean floor_lamp)
)
    (:goal
    (and
        (on light)
        (plugged_in light)
    )
)
    )
    