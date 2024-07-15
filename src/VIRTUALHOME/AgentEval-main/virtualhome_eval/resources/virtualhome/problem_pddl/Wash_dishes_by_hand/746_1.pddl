(define (problem Wash_dishes_by_hand)
    (:domain virtualhome)
    (:objects
    character - character
    dish_soap dining_room home_office drinking_glass water sponge sink - object
)
    (:init
    (containers sink)
    (recipient sink)
    (cream dish_soap)
    (grabbable dish_soap)
    (movable dish_soap)
    (pourable dish_soap)
    (drinkable water)
    (pourable water)
    (grabbable sponge)
    (movable sponge)
    (grabbable drinking_glass)
    (movable drinking_glass)
    (pourable drinking_glass)
    (recipient drinking_glass)
    (inside character home_office)
    (next_to water sponge)
    (next_to sponge water)
)
    (:goal
    (and
    )
)
    )
    