(define (problem Wash_hands)
    (:domain virtualhome)
    (:objects
    character - character
    faucet hands_both bedroom bathroom towel sink bathroom_counter soap - object
)
    (:init
    (surfaces bathroom_counter)
    (containers sink)
    (recipient sink)
    (has_switch faucet)
    (body_part hands_both)
    (cream soap)
    (grabbable soap)
    (movable soap)
    (cover_object towel)
    (grabbable towel)
    (movable towel)
    (next_to sink soap)
    (next_to sink towel)
    (next_to soap sink)
    (next_to towel sink)
    (inside character bedroom)
)
    (:goal
    (and
    )
)
    )
    