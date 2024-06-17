(define (problem Wash_hands)
    (:domain virtualhome)
    (:objects
    character - character
    faucet dining_room bedroom water sink kitchen_counter soap - object
)
    (:init
    (clean faucet)
    (off faucet)
    (surfaces kitchen_counter)
    (containers sink)
    (recipient sink)
    (has_switch faucet)
    (cream soap)
    (grabbable soap)
    (movable soap)
    (drinkable water)
    (pourable water)
    (next_to soap sink)
    (inside character bedroom)
    (next_to sink soap)
)
    (:goal
    (and
    )
)
    )
    