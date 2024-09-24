(define (problem Go_to_sleep)
    (:domain virtualhome)
    (:objects
    character - character
    bed bathroom bedroom - object
)
    (:init
    (lieable bed)
    (inside_room bed bedroom)
    (inside character bathroom)
    (sittable bed)
    (surfaces bed)
)
    (:goal
    (and
        (lying character)
        (ontop character bed)
    )
)
    )
    