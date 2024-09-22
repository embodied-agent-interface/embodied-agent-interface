(define (problem Go_to_toilet)
    (:domain virtualhome)
    (:objects
    character - character
    dining_room bathroom toilet - object
)
    (:init
    (can_open toilet)
    (sittable toilet)
    (sitting character)
    (containers toilet)
    (inside_room toilet bathroom)
    (inside character dining_room)
)
    (:goal
    (and
        (inside character bathroom)
        (facing character toilet)
    )
)
    )
    