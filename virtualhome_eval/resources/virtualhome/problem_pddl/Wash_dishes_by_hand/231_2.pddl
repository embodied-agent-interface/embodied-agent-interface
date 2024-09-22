(define (problem Wash_dishes_by_hand)
    (:domain virtualhome)
    (:objects
    character - character
    dish_soap plate dining_room home_office water - object
)
    (:init
    (grabbable plate)
    (movable plate)
    (recipient plate)
    (surfaces plate)
    (cream dish_soap)
    (grabbable dish_soap)
    (movable dish_soap)
    (pourable dish_soap)
    (drinkable water)
    (pourable water)
    (next_to water plate)
    (next_to dish_soap plate)
    (next_to plate water)
    (inside character home_office)
    (next_to plate dish_soap)
)
    (:goal
    (and
    )
)
    )
    