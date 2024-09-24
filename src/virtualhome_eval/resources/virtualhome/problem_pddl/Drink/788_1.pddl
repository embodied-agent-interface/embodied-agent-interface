(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom kitchen_cabinet faucet water sink kitchen_counter dining_room drinking_glass - object
)
    (:init
    (containers sink)
    (inside_room water dining_room)
    (obj_next_to sink water)
    (obj_next_to sink kitchen_counter)
    (inside_room sink bathroom)
    (grabbable drinking_glass)
    (inside_room faucet dining_room)
    (pourable water)
    (obj_next_to water sink)
    (obj_inside drinking_glass kitchen_cabinet)
    (inside_room sink dining_room)
    (obj_next_to sink faucet)
    (off faucet)
    (inside_room kitchen_counter dining_room)
    (obj_ontop faucet sink)
    (closed kitchen_cabinet)
    (surfaces kitchen_cabinet)
    (pourable drinking_glass)
    (obj_next_to drinking_glass kitchen_cabinet)
    (obj_next_to sink drinking_glass)
    (clean kitchen_cabinet)
    (obj_next_to kitchen_counter faucet)
    (surfaces kitchen_counter)
    (inside_room faucet bathroom)
    (drinkable water)
    (movable drinking_glass)
    (has_switch faucet)
    (obj_next_to kitchen_cabinet drinking_glass)
    (obj_ontop faucet kitchen_counter)
    (recipient drinking_glass)
    (obj_next_to faucet kitchen_counter)
    (clean faucet)
    (containers kitchen_cabinet)
    (recipient sink)
    (inside_room kitchen_cabinet dining_room)
    (inside character bathroom)
    (obj_next_to drinking_glass sink)
    (obj_next_to faucet sink)
    (can_open kitchen_cabinet)
    (obj_next_to kitchen_counter sink)
    (inside_room drinking_glass dining_room)
    (obj_inside sink kitchen_counter)
)
    (:goal
    (and
        (holds_rh character drinking_glass)
    )
)
    )
    