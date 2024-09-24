(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    couch sheets - object
)
    (:init
    (lieable couch)
    (obj_next_to sheets couch)
    (surfaces couch)
    (cover_object sheets)
    (movable sheets)
    (movable couch)
    (obj_next_to couch sheets)
    (grabbable sheets)
    (sittable couch)
)
    (:goal
    (and
        (sitting character)
        (ontop character couch)
    )
)
    )
    