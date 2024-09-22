(define (problem Wash_hands)
    (:domain virtualhome)
    (:objects
    character - character
    faucet dining_room bathroom towel sink bathroom_counter soap - object
)
    (:init
    (surfaces bathroom_counter)
    (containers sink)
    (recipient sink)
    (has_switch faucet)
    (cream soap)
    (grabbable soap)
    (movable soap)
    (cover_object towel)
    (grabbable towel)
    (movable towel)
    (next_to sink towel)
    (inside character dining_room)
    (next_to soap sink)
    (next_to towel sink)
    (next_to sink soap)
)
    (:goal
    (and
    )
)
    )
    