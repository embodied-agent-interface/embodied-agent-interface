(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    novel home_office light table chair dining_room - object
)
    (:init
    (surfaces chair)
    (has_plug light)
    (has_switch light)
    (surfaces table)
    (readable novel)
    (obj_next_to light novel)
    (movable chair)
    (plugged_in light)
    (sittable chair)
    (obj_next_to light light)
    (obj_next_to light chair)
    (obj_inside novel home_office)
    (has_paper novel)
    (obj_next_to light table)
    (movable table)
    (obj_next_to table light)
    (obj_next_to novel light)
    (clean light)
    (movable novel)
    (cuttable novel)
    (obj_next_to chair table)
    (grabbable chair)
    (obj_next_to chair light)
    (inside character dining_room)
    (grabbable novel)
    (inside_room table dining_room)
    (can_open novel)
    (obj_next_to table chair)
    (off light)
    (obj_inside table home_office)
    (obj_inside chair home_office)
    (inside_room light dining_room)
    (obj_inside light home_office)
)
    (:goal
    (and
        (holds_rh character novel)
    )
)
    )
    