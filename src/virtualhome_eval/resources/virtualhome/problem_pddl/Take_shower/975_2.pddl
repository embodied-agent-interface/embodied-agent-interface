(define (problem Take_shower)
    (:domain virtualhome)
    (:objects
    character - character
    shower bathroom bedroom - object
)
    (:init
    (inside character bedroom)
    (inside_room shower bathroom)
)
    (:goal
    (and
        (next_to character shower)
    )
)
    )
    