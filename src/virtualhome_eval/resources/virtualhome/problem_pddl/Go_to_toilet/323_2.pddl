(define (problem Go_to_toilet)
    (:domain virtualhome)
    (:objects
    character - character
    bathroom toilet home_office - object
)
    (:init
    (clean toilet)
    (can_open toilet)
    (closed toilet)
    (containers toilet)
    (sittable toilet)
    (off toilet)
    (inside_room toilet bathroom)
    (inside character home_office)
)
    (:goal
    (and
        (ontop character toilet)
    )
)
    )
    