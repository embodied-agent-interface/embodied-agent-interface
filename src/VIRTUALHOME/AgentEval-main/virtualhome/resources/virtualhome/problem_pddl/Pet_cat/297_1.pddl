(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    home_office couch dining_room cat - object
)
    (:init
    (grabbable cat)
    (obj_inside cat home_office)
    (lieable couch)
    (obj_next_to cat couch)
    (surfaces couch)
    (obj_next_to couch cat)
    (movable couch)
    (obj_inside couch home_office)
    (inside character dining_room)
    (movable cat)
    (sittable couch)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    