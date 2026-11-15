# Progress

## Current state
commit: e910a0f
tests: 10/19 passed
shift: 4

## Completed
- add_subtract: add(a, b) and subtract(a, b)

## In progress
- multiply_divide [75%]

## Known issues
- multiply_divide: test_divide_by_zero_raises_value_error - ValueError: Cannot divide by zero

## Next steps
- multiply_divide: multiply(a, b) and divide(a, b)
- power_modulo: power(a, b) and modulo(a, b)
- parse_expression: calculate("2 + 3") splits "a op b" into 3 tokens (ops + - * / ** %) and calls the functions above

## Notes for next shift
Here is a note for the next engineer: This shift, the multiply_divide step failed after 3 attempts due to a division by zero error. Be cautious when testing the test_divide_by_zero_raises_value_error test, as it is currently failing.
