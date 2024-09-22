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

    (:action walk_towards
        :parameters (?char - character ?obj - object)
        :precondition (and
                      (not (sitting ?char))
                      (not (lying ?char))
        )
        :effect (and
                (next_to ?char ?obj)
                (forall (?far_obj - object) 
                    (when (not (obj_next_to ?far_obj ?obj)) (not (next_to ?char ?far_obj)))
                )
                (forall (?close_obj - object)
                    (when (obj_next_to ?close_obj ?obj) (next_to ?char ?close_obj))
                )
                )
    )
    (:action walk_into
        :parameters (?char - character ?room - object)
        :precondition (and
                      (not (sitting ?char))
                      (not (lying ?char))
        )
        :effect (and
                (inside ?char ?room)
                (forall (?far_obj - object) 
                    (when (not (inside_room ?far_obj ?room)) (not (next_to ?char ?far_obj)))
                )
        )
    )
    (:action find
        :parameters (?char - character ?obj - object)
        :precondition (next_to ?char ?obj)
        :effect ()
    )
    (:action sit
        :parameters (?char - character ?obj - object)
        :precondition (and
                      (next_to ?char ?obj)
                      (sittable ?obj)
                      (not (sitting ?char))
        )
        :effect (and
                (sitting ?char)
                (ontop ?char ?obj)
        ) 
    )
    (:action standup
        :parameters (?char - character)
        :precondition (or 
                      (sitting ?char)
                      (lying ?char)
        )
        :effect (and 
                (not (sitting ?char))
                (not (lying ?char))
        )
    )
    (:action grab
        :parameters (?char - character ?obj - object)
        :precondition (and
                      (grabbable ?obj)
                      (next_to ?char ?obj)
                      (not (exists (?obj2 - object) (and (obj_inside ?obj ?obj2) (closed ?obj2))))
                      (not (and (exists (?obj3 - object) (holds_lh ?char ?obj3)) (exists (?obj4 - object) (holds_rh ?char ?obj4))))
                      )
        :effect (and
                (when (exists (?obj3 - object) (holds_lh ?char ?obj3)) (holds_rh ?char ?obj))
                (when (exists (?obj4 - object) (holds_rh ?char ?obj4)) (holds_lh ?char ?obj))
                (when 
                    (not (and (exists (?obj3 - object) (holds_lh ?char ?obj3)) (exists (?obj4 - object) (holds_rh ?char ?obj4))))
                    (holds_rh ?char ?obj)
                )
        ) 
    )
    (:action open
        :parameters (?char - character ?obj - object)
        :precondition (and
                      (can_open ?obj)
                      (closed ?obj)
                      (next_to ?char ?obj)
                      (not (on ?obj))
        )  
        :effect (and
                (open ?obj)
                (not (closed ?obj))
        ) 
    )
    (:action close
        :parameters (?char - character ?obj - object)
        :precondition (and
                      (can_open ?obj)
                      (open ?obj)
                      (next_to ?char ?obj)
        )
        :effect (and
                (closed ?obj)
                (not (on ?obj))
        ) 
    )
    (:action put_on
        :parameters (?char - character ?obj1 - object ?obj2 - object)
        :precondition (or
                        (and
                        (next_to ?char ?obj2)
                        (holds_lh ?char ?obj1)
                        )
                        (and
                        (next_to ?char ?obj2)
                        (holds_rh ?char ?obj1)
                        )
        )
        :effect (and
                (obj_next_to ?obj1 ?obj2)
                (obj_ontop ?obj1 ?obj2)
                (not (holds_lh ?char ?obj1))
                (not (holds_rh ?char ?obj1))
        )
    )
    (:action put_on_character
        :parameters (?char - character ?obj - object)
        :precondition (or
                        (holds_lh ?char ?obj)
                        (holds_rh ?char ?obj)
                    )
        :effect (and
                (on_char ?obj ?char)
                (not (holds_lh ?char ?obj))
                (not (holds_rh ?char ?obj))
        )
    )
    (:action put_inside
        :parameters (?char - character ?obj1 - object ?obj2 - object)
        :precondition (or
                        (and
                        (next_to ?char ?obj2)
                        (holds_lh ?char ?obj1)
                        (not (can_open ?obj2))
                        )
                        (and
                        (next_to ?char ?obj2)
                        (holds_lh ?char ?obj1)
                        (open ?obj2)
                        )
                        (and
                        (next_to ?char ?obj2)
                        (holds_rh ?char ?obj1)
                        (not (can_open ?obj2))
                        )
                        (and
                        (next_to ?char ?obj2)
                        (holds_rh ?char ?obj1)
                        (open ?obj2)
                        )
        )
        :effect (and
                (obj_inside ?obj1 ?obj2)
                (not (holds_lh ?char ?obj1))
                (not (holds_rh ?char ?obj1))
        ) 
    )
    (:action switch_on
        :parameters (?char - character ?obj - object)
        :precondition (and
                      (has_switch ?obj)
                      (off ?obj)
                      (plugged_in ?obj)
                      (next_to ?char ?obj)
                      
        )  
        :effect (and
                (on ?obj)
                (not (off ?obj))
        ) 
    )
    (:action switch_off
        :parameters (?char - character ?obj - object)
        :precondition (and
                      (has_switch ?obj)
                      (on ?obj)
                      (next_to ?char ?obj)                  
        )  
        :effect (and
                (off ?obj)
                (not (on ?obj))
        ) 
    )
    (:action drink
        :parameters (?char - character ?obj - object)
        :precondition (or
                      (and
                      (drinkable ?obj)
                      (holds_lh ?char ?obj)
                      )
                      (and
                      (drinkable ?obj)
                      (holds_rh ?char ?obj)
                      )
                      (and
                      (recipient ?obj)
                      (holds_lh ?char ?obj)
                      )
                      (and
                      (recipient ?obj)
                      (holds_rh ?char ?obj)
                      )
        )  
        :effect () 
    )
    (:action turn_to
        :parameters (?char - character ?obj - object)
        :precondition ()                  
        :effect (facing ?char ?obj)
    )
    (:action look_at
        :parameters (?char - character ?obj - object)
        :precondition (facing ?char ?obj)                  
        :effect () 
    )
    (:action wipe
        :parameters (?char - character ?obj1 - object ?obj2 - object)
        :precondition (or
                      (and 
                      (next_to ?char ?obj1) 
                      (holds_lh ?char ?obj2)
                      )
                      (and 
                      (next_to ?char ?obj1) 
                      (holds_rh ?char ?obj2)
                      )
        )
        :effect (and 
                (clean ?obj1)
                (not (dirty ?obj1))
        )
    )
    (:action drop
        :parameters (?char - character ?obj - object ?room - object)
        :precondition (or
                      (and 
                      (holds_lh ?char ?obj)
                      (obj_inside ?obj ?room)
                      )
                      (and 
                      (holds_rh ?char ?obj)
                      (obj_inside ?obj ?room)
                      )
        )               
        :effect (and
                (not (holds_lh ?char ?obj))
                (not (holds_rh ?char ?obj))
        ) 
    )
    (:action read 
        :parameters (?char - character ?obj - object)
        :precondition (or
                      (and 
                      (readable ?obj) 
                      (holds_lh ?char ?obj)
                      )
                      (and 
                      (readable ?obj) 
                      (holds_rh ?char ?obj)
                      )
        )
        :effect ()
    )
    (:action touch 
        :parameters (?char - character ?obj - object)
        :precondition (or
                      (and 
                      (readable ?obj) 
                      (holds_lh ?char ?obj)
                      (not (exists (?obj2 - object) (and (obj_inside ?obj ?obj2) (closed ?obj2))))
                      )
                      (and 
                      (readable ?obj) 
                      (holds_rh ?char ?obj)
                      (not (exists (?obj2 - object) (and (obj_inside ?obj ?obj2) (closed ?obj2))))
                      )
        )
        :effect ()
    )
    (:action lie 
        :parameters (?char - character ?obj - object)
        :precondition (and 
                      (lieable ?obj) 
                      (next_to ?char ?obj)
                      (not (lying ?char))
        )
        :effect (and
                (lying ?char)
                (ontop ?char ?obj)
                (not (sitting ?char))
        )
    )
    (:action pour 
        :parameters (?char - character ?obj1 - object ?obj2 - object)
        :precondition (or
                      (and 
                      (pourable ?obj1) 
                      (holds_lh ?char ?obj1)
                      (recipient ?obj2)
                      (next_to ?char ?obj2)
                      )
                      (and 
                      (pourable ?obj1) 
                      (holds_rh ?char ?obj1)
                      (recipient ?obj2)
                      (next_to ?char ?obj2)
                      )
                      (and 
                      (drinkable ?obj1) 
                      (holds_lh ?char ?obj1)
                      (recipient ?obj2)
                      (next_to ?char ?obj2)
                      )
                      (and 
                      (drinkable ?obj1) 
                      (holds_rh ?char ?obj1)
                      (recipient ?obj2)
                      (next_to ?char ?obj2)
                      )     
        )
        :effect (obj_inside ?obj1 ?obj2)
    )
    (:action type 
        :parameters (?char - character ?obj - object)
        :precondition (and 
                      (has_switch ?obj) 
                      (next_to ?char ?obj)
        )
        :effect ()
    )
    (:action watch 
        :parameters (?char - character ?obj - object)
        :precondition (and 
                      (lookable ?obj) 
                      (facing ?char ?obj)
                      (not (exists (?obj2 - object) (and (obj_inside ?obj ?obj2) (closed ?obj2))))
        )
        :effect ()
    )
    (:action move 
        :parameters (?char - character ?obj - object)
        :precondition (and 
                      (movable ?obj) 
                      (next_to ?char ?obj)
                      (not (exists (?obj2 - object) (and (obj_inside ?obj ?obj2) (closed ?obj2))))
        )
        :effect ()
    )
    (:action wash 
        :parameters (?char - character ?obj - object)
        :precondition (and 
                      (next_to ?char ?obj)
        )
        :effect (and
                (clean ?obj)
                (not (dirty ?obj))
        )
    )
    (:action squeeze 
        :parameters (?char - character ?obj - object)
        :precondition (and 
                      (next_to ?char ?obj)
                      (clothes ?obj)
        )
        :effect ()
    )
    (:action plug_in 
        :parameters (?char - character ?obj - object)
        :precondition (or
                        (and 
                        (next_to ?char ?obj)
                        (has_plug ?obj)
                        (plugged_out ?obj)
                        )
                        (and 
                        (next_to ?char ?obj)
                        (has_switch ?obj)
                        (plugged_out ?obj)
                        )
                      )
        :effect (and
                (plugged_in ?obj)
                (not (plugged_out ?obj))
        )
    )
    (:action plug_out 
        :parameters (?char - character ?obj - object)
        :precondition (and 
                      (next_to ?char ?obj)
                      (has_plug ?obj)
                      (plugged_in ?obj)
                      (not (on ?obj))
        )
        :effect (and
                (plugged_out ?obj)
                (not (plugged_in ?obj))
        )
    )
    (:action cut 
        :parameters (?char - character ?obj - object)
        :precondition (and 
                      (next_to ?char ?obj)
                      (eatable ?obj)
                      (cuttable ?obj)
        )
        :effect ()
    )
    (:action eat 
        :parameters (?char - character ?obj - object)
        :precondition (and 
                      (next_to ?char ?obj)
                      (eatable ?obj)
        )
        :effect ()
    )
    (:action sleep 
        :parameters (?char - character ?obj - object)
        :precondition (or 
                      (lying ?char)
                      (sitting ?char)
        )
        :effect ()
    )
    (:action wake_up 
        :parameters (?char - character ?obj - object)
        :precondition (or 
                      (lying ?char)
                      (sitting ?char)
        )
        :effect ()
    )
)