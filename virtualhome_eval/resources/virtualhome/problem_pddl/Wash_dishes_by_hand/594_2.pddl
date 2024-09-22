(define (problem Wash_dishes_by_hand)
    (:domain virtualhome)
    (:objects
    character - character
    dish_soap bathroom_counter plate sink - object
)
    (:init
    (surfaces bathroom_counter)
    (containers sink)
    (recipient sink)
    (cream dish_soap)
    (grabbable dish_soap)
    (movable dish_soap)
    (pourable dish_soap)
    (grabbable plate)
    (movable plate)
    (recipient plate)
    (surfaces plate)
    (ontop dish_soap sink)
    (next_to sink dish_soap)
    (next_to dish_soap sink)
)
    (:goal
    (and
    )
)
    )
    