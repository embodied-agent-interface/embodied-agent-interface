(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    novel home_office couch coffee_cup dining_room - object
)
    (:init
    (grabbable coffee_cup)
    (surfaces couch)
    (obj_inside couch home_office)
    (obj_inside coffee_cup home_office)
    (readable novel)
    (recipient coffee_cup)
    (movable coffee_cup)
    (obj_next_to coffee_cup couch)
    (lieable couch)
    (obj_inside novel home_office)
    (has_paper novel)
    (obj_next_to couch novel)
    (movable novel)
    (cuttable novel)
    (pourable coffee_cup)
    (inside character dining_room)
    (movable couch)
    (grabbable novel)
    (obj_next_to novel couch)
    (sittable couch)
    (can_open novel)
    (obj_next_to couch coffee_cup)
)
    (:goal
    (and
        (sitting character)
        (ontop character couch)
    )
)
    )
    