(define (problem Pet_cat)
    (:domain virtualhome)
    (:objects
    character - character
    home_office cat hair couch bedroom - object
)
    (:init
    (grabbable cat)
    (obj_inside cat home_office)
    (lieable couch)
    (movable hair)
    (obj_next_to cat couch)
    (grabbable hair)
    (surfaces couch)
    (inside character bedroom)
    (obj_next_to couch cat)
    (movable couch)
    (body_part hair)
    (cuttable hair)
    (movable cat)
    (obj_inside couch home_office)
    (sittable couch)
)
    (:goal
    (and
        (next_to character cat)
    )
)
    )
    