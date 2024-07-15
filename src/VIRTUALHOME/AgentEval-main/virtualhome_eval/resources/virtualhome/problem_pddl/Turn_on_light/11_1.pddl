(define (problem Turn_on_light)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom dining_room floor_lamp - object
)
    (:init
    (has_switch floor_lamp)
    (plugged_out floor_lamp)
    (inside_room floor_lamp bedroom)
    (off floor_lamp)
    (movable floor_lamp)
    (inside character dining_room)
    (clean floor_lamp)
)
    (:goal
    (and
        (on floor_lamp)
    )
)
    )
    