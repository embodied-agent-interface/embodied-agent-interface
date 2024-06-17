(define (problem Listen_to_music)
    (:domain virtualhome)
    (:objects
    character - character
    bedroom home_office cd_player headset - object
)
    (:init
    (grabbable headset)
    (sitting character)
    (movable cd_player)
    (obj_next_to cd_player headset)
    (obj_next_to headset cd_player)
    (inside_room cd_player bedroom)
    (has_switch cd_player)
    (plugged_out cd_player)
    (closed cd_player)
    (clean cd_player)
    (off cd_player)
    (movable headset)
    (inside_room headset bedroom)
    (grabbable cd_player)
    (surfaces cd_player)
    (inside character home_office)
    (clothes headset)
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
    