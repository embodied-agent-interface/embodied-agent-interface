(define (problem Pick_up_phone)
    (:domain virtualhome)
    (:objects
    character - character
    home_office phone couch table food_food dining_room - object
)
    (:init
    (inside_room food_food dining_room)
    (obj_inside food_food home_office)
    (inside_room phone dining_room)
    (obj_next_to table food_food)
    (grabbable phone)
    (surfaces couch)
    (surfaces table)
    (sitting character)
    (has_switch phone)
    (obj_inside couch home_office)
    (obj_next_to phone table)
    (movable phone)
    (obj_inside phone home_office)
    (lieable couch)
    (movable food_food)
    (obj_ontop phone table)
    (movable table)
    (obj_ontop food_food table)
    (grabbable food_food)
    (obj_next_to table phone)
    (inside character dining_room)
    (movable couch)
    (eatable food_food)
    (obj_next_to table couch)
    (sittable couch)
    (inside_room table dining_room)
    (has_plug phone)
    (obj_inside table home_office)
    (obj_next_to couch table)
    (obj_inside table couch)
    (obj_next_to food_food table)
    (cuttable food_food)
)
    (:goal
    (and
        (holds_rh character phone)
    )
)
    )
    