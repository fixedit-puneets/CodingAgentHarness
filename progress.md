# Progress

## Current state
commit: e3261ea
tests: 10/19 passed
shift: 2

## Completed
- add_subtract: add(a, b) and subtract(a, b)

## In progress
- multiply_divide [75%]

## Known issues
- multiply_divide: test_divide - AssertionError: 2 != 2.5

## Next steps
- multiply_divide: multiply(a, b) and divide(a, b)
- power_modulo: power(a, b) and modulo(a, b)
- parse_expression: calculate("2 + 3") splits "a op b" into 3 tokens (ops + - * / ** %) and calls the functions above

## Notes for next shift
Here is a note for the next engineer: This shift, the multiply_divide step failed after 3 attempts due to issues with the test_divide function. Be cautious when running this step, as it is currently failing and may require further investigation.
