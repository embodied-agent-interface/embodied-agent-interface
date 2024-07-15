(define (problem Write_an_email)
    (:domain virtualhome)
    (:objects
    character - character
    keyboard computer mousepad home_office bedroom mouse desk chair cpuscreen - object
)
    (:init
    (clean computer)
    (off computer)
    (grabbable chair)
    (movable chair)
    (sittable chair)
    (surfaces chair)
    (movable desk)
    (surfaces desk)
    (grabbable mouse)
    (has_plug mouse)
    (movable mouse)
    (movable mousepad)
    (surfaces mousepad)
    (grabbable keyboard)
    (has_plug keyboard)
    (movable keyboard)
    (has_switch computer)
    (lookable computer)
    (inside character bedroom)
)
    (:goal
    (and
        (on computer)
    )
)
    )
    