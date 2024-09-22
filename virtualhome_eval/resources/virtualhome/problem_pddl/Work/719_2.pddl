(define (problem Work)
    (:domain virtualhome)
    (:objects
    character - character
    home_office keyboard computer chair dining_room - object
)
    (:init
    (surfaces chair)
    (obj_next_to chair keyboard)
    (obj_next_to keyboard computer)
    (plugged_out computer)
    (obj_next_to computer keyboard)
    (has_plug keyboard)
    (facing chair computer)
    (movable chair)
    (obj_next_to computer chair)
    (sittable chair)
    (has_switch computer)
    (obj_next_to keyboard chair)
    (grabbable keyboard)
    (obj_inside keyboard home_office)
    (grabbable chair)
    (inside character dining_room)
    (lookable computer)
    (clean computer)
    (off computer)
    (obj_inside computer home_office)
    (obj_inside chair home_office)
    (movable keyboard)
    (obj_next_to chair computer)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    