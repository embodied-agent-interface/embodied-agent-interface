(define (problem Wash_hands)
    (:domain virtualhome)
    (:objects
    character - character
    faucet dining_room hands_both bathroom towel sink bathroom_counter soap - object
)
    (:init
    (surfaces bathroom_counter)
    (containers sink)
    (recipient sink)
    (has_switch faucet)
    (cream soap)
    (grabbable soap)
    (movable soap)
    (body_part hands_both)
    (cover_object towel)
    (grabbable towel)
    (movable towel)
    (body_part hands_both)
    (inside character dining_room)
    (next_to soap sink)
    (next_to sink towel)
    (next_to towel sink)
    (next_to sink soap)
)
    (:goal
    (and
    )
)
    )
    