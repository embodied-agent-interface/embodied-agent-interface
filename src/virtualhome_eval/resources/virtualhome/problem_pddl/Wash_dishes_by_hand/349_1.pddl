(define (problem Wash_dishes_by_hand)
    (:domain virtualhome)
    (:objects
    character - character
    faucet dish_soap plate dining_room bathroom - object
)
    (:init
    (clean faucet)
    (off faucet)
    (has_switch faucet)
    (cream dish_soap)
    (grabbable dish_soap)
    (movable dish_soap)
    (pourable dish_soap)
    (grabbable plate)
    (movable plate)
    (recipient plate)
    (surfaces plate)
    (next_to plate faucet)
    (next_to dish_soap faucet)
    (inside character bathroom)
    (next_to faucet dish_soap)
    (next_to faucet plate)
)
    (:goal
    (and
    )
)
    )
    