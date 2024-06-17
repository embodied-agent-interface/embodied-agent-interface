(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    home_office computer dining_room chair - object
)
    (:init
    (obj_next_to computer chair)
    (off computer)
    (sittable chair)
    (obj_next_to chair computer)
    (surfaces chair)
    (has_switch computer)
    (obj_inside computer home_office)
    (grabbable chair)
    (plugged_out computer)
    (inside character dining_room)
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
    