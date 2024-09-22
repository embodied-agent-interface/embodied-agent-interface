(define (problem Wash_hands)
    (:domain virtualhome)
    (:objects
    character - character
    faucet dining_room hands_both bathroom soap - object
)
    (:init
    (has_switch faucet)
    (cream soap)
    (grabbable soap)
    (movable soap)
    (body_part hands_both)
    (next_to faucet soap)
    (inside character dining_room)
    (next_to soap faucet)
)
    (:goal
    (and
    )
)
    )
    