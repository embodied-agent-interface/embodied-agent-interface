(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom home_office floor_lamp - object
)
    (:init
    (has_switch floor_lamp)
    (obj_inside floor_lamp home_office)
    (plugged_out floor_lamp)
    (inside character bathroom)
    (off floor_lamp)
    (movable floor_lamp)
    (clean floor_lamp)
)
    (:goal
    (and
        (on floor_lamp)
    )
)
    )
    