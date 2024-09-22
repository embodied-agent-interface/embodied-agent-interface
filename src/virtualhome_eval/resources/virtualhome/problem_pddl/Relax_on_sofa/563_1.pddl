(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    couch - object
)
    (:init
    (surfaces couch)
    (lieable couch)
    (sittable couch)
    (movable couch)
)
    (:goal
    (and
        (lying character)
        (ontop character couch)
    )
)
    )
    