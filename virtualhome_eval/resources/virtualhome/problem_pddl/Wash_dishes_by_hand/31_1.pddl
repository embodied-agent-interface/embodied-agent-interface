(define (problem Wash_dishes_by_hand)
    (:domain virtualhome)
    (:objects
    character - character
    faucet dish_soap plate bowl dining_room bedroom sponge dishrack sink kitchen_counter - object
)
    (:init
    (surfaces kitchen_counter)
    (containers sink)
    (recipient sink)
    (has_switch faucet)
    (cream dish_soap)
    (grabbable dish_soap)
    (movable dish_soap)
    (pourable dish_soap)
    (grabbable bowl)
    (movable bowl)
    (recipient bowl)
    (grabbable sponge)
    (movable sponge)
    (grabbable dishrack)
    (movable dishrack)
    (surfaces dishrack)
    (grabbable plate)
    (movable plate)
    (recipient plate)
    (surfaces plate)
    (next_to plate sink)
    (next_to sponge sink)
    (next_to dish_soap sink)
    (next_to sink sponge)
    (next_to sink bowl)
    (next_to sink dish_soap)
    (next_to bowl sink)
    (inside character bedroom)
    (next_to sink plate)
)
    (:goal
    (and
    )
)
    )
    