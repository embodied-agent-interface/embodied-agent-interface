(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office chair computer - object
)
    (:init
    (obj_next_to computer chair)
    (off computer)
    (sittable chair)
    (obj_next_to chair computer)
    (surfaces chair)
    (has_switch computer)
    (inside_room chair bedroom)
    (obj_inside computer home_office)
    (inside character bedroom)
    (grabbable chair)
    (plugged_out computer)
    (inside_room computer bedroom)
    (obj_inside chair home_office)
    (lookable computer)
    (facing chair computer)
    (clean computer)
    (movable chair)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    