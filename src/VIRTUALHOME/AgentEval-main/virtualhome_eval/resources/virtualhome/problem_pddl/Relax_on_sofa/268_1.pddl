(define (problem Relax_on_sofa)
    (:domain virtualhome)
    (:objects
    character - character
    home_office couch light television dining_room - object
)
    (:init
    (has_plug television)
    (has_switch light)
    (has_plug light)
    (surfaces couch)
    (inside_room television dining_room)
    (obj_inside couch home_office)
    (plugged_in light)
    (lieable couch)
    (obj_next_to couch television)
    (obj_next_to light light)
    (lookable television)
    (clean light)
    (inside character dining_room)
    (movable couch)
    (facing couch television)
    (sittable couch)
    (has_switch television)
    (off light)
    (facing light television)
    (obj_inside television home_office)
    (obj_next_to television couch)
    (inside_room light dining_room)
    (obj_inside light home_office)
)
    (:goal
    (and
        (sitting character)
        (ontop character couch)
    )
)
    )
    