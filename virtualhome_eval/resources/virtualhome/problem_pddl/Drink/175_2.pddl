(define (problem Drink)
    (:domain virtualhome)
    (:objects
    character - character
    home_office faucet cup sink kitchen_counter dining_room - object
)
    (:init
    (containers sink)
    (obj_next_to sink kitchen_counter)
    (recipient cup)
    (movable cup)
    (inside_room cup dining_room)
    (inside_room faucet dining_room)
    (grabbable cup)
    (inside_room sink dining_room)
    (obj_next_to sink faucet)
    (obj_ontop faucet sink)
    (inside_room kitchen_counter dining_room)
    (obj_next_to sink cup)
    (obj_next_to cup sink)
    (obj_next_to kitchen_counter faucet)
    (surfaces kitchen_counter)
    (has_switch faucet)
    (obj_ontop faucet kitchen_counter)
    (obj_next_to faucet kitchen_counter)
    (recipient sink)
    (inside character home_office)
    (obj_next_to faucet sink)
    (obj_next_to kitchen_counter sink)
    (pourable cup)
    (obj_inside sink kitchen_counter)
)
    (:goal
    (and
        (holds_rh character cup)
    )
)
    )
    