(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    home_office kitchen_cabinet water_glass faucet dining_room - object
)
    (:init
    (inside_room faucet dining_room)
    (obj_inside water_glass kitchen_cabinet)
    (obj_next_to faucet kitchen_cabinet)
    (off faucet)
    (movable water_glass)
    (pourable water_glass)
    (inside_room water_glass dining_room)
    (obj_next_to kitchen_cabinet faucet)
    (closed kitchen_cabinet)
    (surfaces kitchen_cabinet)
    (obj_next_to water_glass kitchen_cabinet)
    (obj_next_to kitchen_cabinet water_glass)
    (clean kitchen_cabinet)
    (has_switch faucet)
    (clean faucet)
    (containers kitchen_cabinet)
    (inside_room kitchen_cabinet dining_room)
    (recipient water_glass)
    (grabbable water_glass)
    (inside character home_office)
    (can_open kitchen_cabinet)
)
    (:goal
    (and
        (holds_rh character water_glass)
    )
)
    )
    