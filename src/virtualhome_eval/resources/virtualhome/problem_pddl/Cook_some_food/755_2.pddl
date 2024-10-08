(define (problem Cook_some_food)
    (:domain virtualhome)
    (:objects
    character - character
    home_office kitchen_cabinet pasta water oven sauce_pan dining_room - object
)
    (:init
    (obj_next_to kitchen_cabinet oven)
    (obj_next_to kitchen_cabinet water)
    (inside_room water dining_room)
    (off oven)
    (closed oven)
    (pourable water)
    (movable pasta)
    (plugged_in oven)
    (recipient sauce_pan)
    (surfaces sauce_pan)
    (grabbable sauce_pan)
    (obj_inside water kitchen_cabinet)
    (clean oven)
    (obj_next_to kitchen_cabinet sauce_pan)
    (closed kitchen_cabinet)
    (surfaces kitchen_cabinet)
    (obj_inside pasta kitchen_cabinet)
    (obj_inside sauce_pan kitchen_cabinet)
    (clean kitchen_cabinet)
    (has_plug oven)
    (can_open oven)
    (pourable pasta)
    (obj_next_to kitchen_cabinet pasta)
    (containers oven)
    (drinkable water)
    (grabbable pasta)
    (containers kitchen_cabinet)
    (obj_next_to sauce_pan kitchen_cabinet)
    (movable sauce_pan)
    (obj_next_to water kitchen_cabinet)
    (obj_next_to oven kitchen_cabinet)
    (inside_room pasta dining_room)
    (inside_room kitchen_cabinet dining_room)
    (inside_room oven dining_room)
    (containers sauce_pan)
    (inside character home_office)
    (inside_room sauce_pan dining_room)
    (can_open kitchen_cabinet)
    (has_switch oven)
    (obj_next_to pasta kitchen_cabinet)
)
    (:goal
    (and
        (closed oven)
        (on oven)
        (plugged_in oven)
        (obj_ontop sauce_pan oven)
    )
)
    )
    