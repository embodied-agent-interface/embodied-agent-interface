(define (problem Get_some_water)
    (:domain virtualhome)
    (:objects
    character - character
    home_office dining_room cloth_napkin - object
)
    (:init
    (movable cloth_napkin)
    (grabbable cloth_napkin)
    (cuttable cloth_napkin)
    (cover_object cloth_napkin)
    (has_paper cloth_napkin)
    (inside character home_office)
    (inside_room cloth_napkin dining_room)
)
    (:goal
    (and
        (inside character dining_room)
    )
)
    )
    