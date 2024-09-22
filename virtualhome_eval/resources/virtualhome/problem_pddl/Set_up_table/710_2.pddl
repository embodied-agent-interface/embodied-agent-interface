(define (problem Set_up_table)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom kitchen_cabinet table plate dining_room - object
)
    (:init
    (inside_room plate dining_room)
    (recipient plate)
    (obj_next_to kitchen_cabinet plate)
    (surfaces table)
    (obj_next_to plate kitchen_cabinet)
    (grabbable plate)
    (obj_next_to table kitchen_cabinet)
    (closed kitchen_cabinet)
    (surfaces kitchen_cabinet)
    (movable table)
    (clean kitchen_cabinet)
    (surfaces plate)
    (obj_inside plate kitchen_cabinet)
    (obj_next_to kitchen_cabinet table)
    (inside_room table dining_room)
    (containers kitchen_cabinet)
    (movable plate)
    (inside_room kitchen_cabinet dining_room)
    (inside character bathroom)
    (can_open kitchen_cabinet)
)
    (:goal
    (and
        (obj_ontop plate table)
    )
)
    )
    