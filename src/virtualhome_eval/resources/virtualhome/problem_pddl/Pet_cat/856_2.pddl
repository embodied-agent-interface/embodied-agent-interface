(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom couch home_office cat - object
)
    (:init
    (grabbable cat)
    (obj_inside cat home_office)
    (lieable couch)
    (obj_next_to cat couch)
    (surfaces couch)
    (inside character bathroom)
    (obj_next_to couch cat)
    (movable couch)
    (obj_inside couch home_office)
    (movable cat)
    (sittable couch)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    