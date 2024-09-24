(define (problem Wash_hands)
    (:domain virtualhome)
    (:objects
    character - character
    home_office hands_both paper_towel water bathroom sink bathroom_counter soap - object
)
    (:init
    (surfaces bathroom_counter)
    (containers sink)
    (recipient sink)
    (drinkable water)
    (pourable water)
    (cream soap)
    (grabbable soap)
    (movable soap)
    (body_part hands_both)
    (cover_object paper_towel)
    (cuttable paper_towel)
    (grabbable paper_towel)
    (hangable paper_towel)
    (has_paper paper_towel)
    (movable paper_towel)
    (next_to sink soap)
    (next_to paper_towel sink)
    (next_to soap sink)
    (inside character home_office)
    (next_to sink paper_towel)
)
    (:goal
    (and
    )
)
    )
    