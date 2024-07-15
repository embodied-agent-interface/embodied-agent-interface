(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    home_office cat couch television dining_room - object
)
    (:init
    (obj_next_to cat couch)
    (has_plug television)
    (surfaces couch)
    (inside_room television dining_room)
    (obj_inside couch home_office)
    (grabbable cat)
    (lieable couch)
    (obj_next_to couch television)
    (lookable television)
    (obj_inside cat home_office)
    (obj_next_to couch cat)
    (movable couch)
    (inside character dining_room)
    (movable cat)
    (facing couch television)
    (sittable couch)
    (has_switch television)
    (obj_inside television home_office)
    (obj_next_to television couch)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    