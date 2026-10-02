# Week 2 Activity — gather vs as_completed

`as_completed` made it visible that answers can appear in the order they finish rather than the order the questions were submitted; in the clean run, the answer order was different from the question order.

`gather` is useful when all results are needed before moving to the next step, while `as_completed` is useful when results should be processed as soon as each one finishes.