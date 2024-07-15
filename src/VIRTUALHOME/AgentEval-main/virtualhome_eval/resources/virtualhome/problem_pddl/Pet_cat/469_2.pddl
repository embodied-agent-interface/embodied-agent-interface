(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    couch cat - object
)
    (:init
    (grabbable cat)
    (lieable couch)
    (obj_next_to cat couch)
    (surfaces couch)
    (obj_next_to couch cat)
    (movable couch)
    (movable cat)
    (sittable couch)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    