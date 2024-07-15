(define (domain virtualhome)
    (:requirements :typing)
    (:types 
        object character  ; Define 'object' and 'character' as types
    )

    (:predicates
        (closed ?obj - object)  ; obj is closed
        (open ?obj - object)  ; obj is open
        (on ?obj - object)  ; obj is turned on, or it is activated
        (off ?obj - object)  ; obj is turned off, or it is deactivated
        (plugged_in ?obj - object)  ; obj is plugged in
        (plugged_out ?obj - object)  ; obj is unplugged
        (sitting ?char - character)  ; char is sitting, and this represents a state of a character
        (lying ?char - character)  ; char is lying
        (clean ?obj - object)  ; obj is clean
        (dirty ?obj - object)  ; obj is dirty
        (obj_ontop ?obj1 ?obj2 - object)  ; obj1 is on top of obj2
        (ontop ?char - character ?obj - object)  ; char is on obj
        (on_char ?obj - object ?char - character) ; obj is on char
        (inside_room ?obj ?room - object) ; obj is inside room
        (obj_inside ?obj1 ?obj2 - object)  ; obj1 is inside obj2
        (inside ?char - character ?obj - object)  ; char is inside obj
        (obj_next_to ?obj1 ?obj2 - object)  ; obj1 is close to or next to obj2
        (next_to ?char - character ?obj - object) ; char is close to or next to obj
        (between ?obj1 ?obj2 ?obj3 - object)  ; obj1 is between obj2 and obj3
        (facing ?char - character ?obj - object)  ; char is facing obj
        (holds_rh ?char - character ?obj - object)  ; char is holding obj with right hand
        (holds_lh ?char - character ?obj - object)  ; char is holding obj with left hand
        (grabbable ?obj - object)  ; obj can be grabbed
        (cuttable ?obj - object)  ; obj can be cut
        (can_open ?obj - object)  ; obj can be opened
        (readable ?obj - object)  ; obj can be read
        (has_paper ?obj - object)  ; obj has paper
        (movable ?obj - object)  ; obj is movable
        (pourable ?obj - object)  ; obj can be poured from
        (cream ?obj - object)  ; obj is cream
        (has_switch ?obj - object)  ; obj has a switch
        (lookable ?obj - object)  ; obj can be looked at
        (has_plug ?obj - object)  ; obj has a plug
        (drinkable ?obj - object)  ; obj is drinkable
        (body_part ?obj - object)  ; obj is a body part
        (recipient ?obj - object)  ; obj is a recipient
        (containers ?obj - object)  ; obj is a container
        (cover_object ?obj - object)  ; obj is a cover object
        (surfaces ?obj - object)  ; obj has surfaces
        (sittable ?obj - object)  ; obj can be sat on
        (lieable ?obj - object)  ; obj can be lied on
        (person ?obj - object)  ; obj is a person
        (hangable ?obj - object)  ; obj can be hanged
        (clothes ?obj - object)  ; obj is clothes
        (eatable ?obj - object)  ; obj is eatable
        )
