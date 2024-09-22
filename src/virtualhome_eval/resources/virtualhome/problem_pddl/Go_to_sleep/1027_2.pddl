(define (problem Go_to_sleep)
    (:domain virtualhome)
    (:objects
    character - character
    bed bedroom dining_room - object
)
    (:init
    (lieable bed)
    (inside_room bed bedroom)
    (sittable bed)
    (inside character dining_room)
    (surfaces bed)
)
    (:goal
    (and
        (lying character)
        (ontop character bed)
    )
)
    )
    