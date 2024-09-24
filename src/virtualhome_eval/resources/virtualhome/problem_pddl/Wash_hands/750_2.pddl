(define (problem Wash_hands)
    (:domain virtualhome)
    (:objects
    character - character
    hands_both bedroom water bathroom towel sink bathroom_counter soap - object
)
    (:init
    (surfaces bathroom_counter)
    (containers sink)
    (recipient sink)
    (cream soap)
    (grabbable soap)
    (movable soap)
    (drinkable water)
    (pourable water)
    (body_part hands_both)
    (cover_object towel)
    (grabbable towel)
    (movable towel)
    (next_to sink water)
    (next_to towel sink)
    (next_to water sink)
    (next_to sink towel)
    (inside character bedroom)
)
    (:goal
    (and
        (inside water hands_both)
    )
)
    )
    