(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    cd_player - object
)
    (:init
    (plugged_in cd_player)
    (grabbable cd_player)
    (closed cd_player)
    (clean cd_player)
    (off cd_player)
    (movable cd_player)
    (surfaces cd_player)
    (has_switch cd_player)
    (has_plug cd_player)
    (can_open cd_player)
)
    (:goal
    (and
        (closed cd_player)
        (on cd_player)
        (plugged_in cd_player)
    )
)
    )
    