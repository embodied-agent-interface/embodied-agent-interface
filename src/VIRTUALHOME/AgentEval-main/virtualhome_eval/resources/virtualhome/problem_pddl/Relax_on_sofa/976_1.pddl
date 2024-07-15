(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    couch bedroom home_office - object
)
    (:init
    (lieable couch)
    (surfaces couch)
    (inside character bedroom)
    (movable couch)
    (obj_inside couch home_office)
    (sittable couch)
)
    (:goal
    (and
        (lying character)
        (ontop character couch)
    )
)
    )
    