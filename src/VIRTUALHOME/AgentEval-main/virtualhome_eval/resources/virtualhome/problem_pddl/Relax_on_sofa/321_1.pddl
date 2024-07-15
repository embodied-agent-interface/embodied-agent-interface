(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    water_glass couch bedroom home_office - object
)
    (:init
    (lieable couch)
    (surfaces couch)
    (inside character bedroom)
    (obj_next_to couch water_glass)
    (movable water_glass)
    (pourable water_glass)
    (recipient water_glass)
    (grabbable water_glass)
    (obj_inside water_glass home_office)
    (obj_next_to water_glass couch)
    (movable couch)
    (obj_inside couch home_office)
    (sittable couch)
)
    (:goal
    (and
        (sitting character)
        (ontop character couch)
    )
)
    )
    