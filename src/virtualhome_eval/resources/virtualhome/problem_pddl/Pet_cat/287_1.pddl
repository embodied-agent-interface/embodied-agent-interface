(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    cat - object
)
    (:init
    (movable cat)
    (grabbable cat)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    