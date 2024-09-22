(define (problem Go_to_toilet)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom bedroom toilet - object
)
    (:init
    (can_open toilet)
    (inside character bedroom)
    (sittable toilet)
    (containers toilet)
    (inside_room toilet bathroom)
)
    (:goal
    (and
        (inside character bathroom)
        (facing character toilet)
    )
)
    )
    