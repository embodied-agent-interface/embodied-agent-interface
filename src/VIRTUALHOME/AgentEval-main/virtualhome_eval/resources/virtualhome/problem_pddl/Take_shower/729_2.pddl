(define (problem Take_shower)
    (:domain virtualhome)
    (:objects
    character - character
    shower bathroom dining_room - object
)
    (:init
    (inside character dining_room)
    (inside_room shower bathroom)
)
    (:goal
    (and
        (next_to character shower)
    )
)
    )
    