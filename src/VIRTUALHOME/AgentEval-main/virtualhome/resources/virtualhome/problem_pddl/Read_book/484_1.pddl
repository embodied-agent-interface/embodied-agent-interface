(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    novel home_office bedroom chair computer - object
)
    (:init
    (surfaces chair)
    (facing chair computer)
    (readable novel)
    (movable chair)
    (obj_next_to novel chair)
    (obj_next_to computer chair)
    (sittable chair)
    (has_switch computer)
    (obj_inside novel home_office)
    (has_paper novel)
    (obj_next_to chair novel)
    (movable novel)
    (cuttable novel)
    (inside_room chair bedroom)
    (grabbable chair)
    (grabbable novel)
    (lookable computer)
    (can_open novel)
    (obj_inside computer home_office)
    (inside character bedroom)
    (inside_room computer bedroom)
    (obj_inside chair home_office)
    (obj_next_to chair computer)
)
    (:goal
    (and
        (holds_rh character novel)
    )
)
    )
    