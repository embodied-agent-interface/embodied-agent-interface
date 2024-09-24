(define (problem Wash_hands)
    (:domain virtualhome)
    (:objects
    character - character
    faucet home_office hands_both water bathroom - object
)
    (:init
    (has_switch faucet)
    (drinkable water)
    (pourable water)
    (body_part hands_both)
    (inside character home_office)
    (next_to faucet water)
    (next_to water faucet)
)
    (:goal
    (and
        (inside water hands_both)
    )
)
    )
    