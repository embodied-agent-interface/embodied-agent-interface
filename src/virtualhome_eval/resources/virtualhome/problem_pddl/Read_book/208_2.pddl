(define (problem Read_book)
    (:domain virtualhome)
    (:objects
    character - character
    novel home_office hair bedroom floor_lamp - object
)
    (:init
    (obj_inside hair home_office)
    (body_part hair)
    (readable novel)
    (clean floor_lamp)
    (movable hair)
    (has_paper novel)
    (obj_next_to novel floor_lamp)
    (has_switch floor_lamp)
    (movable novel)
    (obj_next_to floor_lamp novel)
    (cuttable novel)
    (off floor_lamp)
    (movable floor_lamp)
    (inside_room novel bedroom)
    (cuttable hair)
    (grabbable novel)
    (can_open novel)
    (plugged_out floor_lamp)
    (grabbable hair)
    (inside_room floor_lamp bedroom)
    (inside character home_office)
)
    (:goal
    (and
        (holds_rh character novel)
    )
)
    )
    