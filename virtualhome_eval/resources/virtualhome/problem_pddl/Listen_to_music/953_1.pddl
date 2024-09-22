(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    music_stand bathroom home_office cd_player - object
)
    (:init
    (surfaces music_stand)
    (obj_next_to music_stand cd_player)
    (obj_next_to cd_player music_stand)
    (can_open music_stand)
    (movable cd_player)
    (containers music_stand)
    (can_open cd_player)
    (has_switch cd_player)
    (obj_inside music_stand home_office)
    (closed cd_player)
    (clean cd_player)
    (off cd_player)
    (obj_inside cd_player home_office)
    (plugged_in cd_player)
    (grabbable cd_player)
    (inside character bathroom)
    (surfaces cd_player)
    (has_plug cd_player)
    (movable music_stand)
)
    (:goal
    (and
        (closed cd_player)
        (on cd_player)
        (plugged_in cd_player)
    )
)
    )
    