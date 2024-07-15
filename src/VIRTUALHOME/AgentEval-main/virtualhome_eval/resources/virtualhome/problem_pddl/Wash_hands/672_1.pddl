(define (problem Wash_hands)
    (:domain virtualhome)
    (:objects
    character - character
    faucet dining_room hands_both bathroom towel soap - object
)
    (:init
    (has_switch faucet)
    (body_part hands_both)
    (cream soap)
    (grabbable soap)
    (movable soap)
    (cover_object towel)
    (grabbable towel)
    (movable towel)
    (next_to towel faucet)
    (inside character dining_room)
    (next_to faucet soap)
    (next_to faucet towel)
    (next_to soap faucet)
)
    (:goal
    (and
    )
)
    )
    