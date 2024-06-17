(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    cat face - object
)
    (:init
    (movable cat)
    (grabbable cat)
    (body_part face)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    