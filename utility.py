

# Returns True if has "number" has (approximately) no more than "significant_digits" significant digits
# This function should NOT be used outside the very specific use case of the RangeAttribute
def check_significant_digits(number: float, significant_digits: int):

    # round up to the smallest possible digit (digits behind that one are seen as "rounding errors" and are neglected)
    number = round(number, significant_digits)

    # Count significant digits in a loop
    reached_significants = False
    count = 0

    for digit in str(number):
        if (not reached_significants and digit in ["0", "."]) or digit == ".":
            continue
        elif not reached_significants:
            reached_significants = True
            count += 1
        else:
            count += 1

    # Count not significant zeros at the end of "number"
    tail_zero_count = 0
    for digit in str(number)[::-1]:
        if digit == ".":
            continue
        if digit == "0":
            tail_zero_count += 1
        else:
            break
    count -= tail_zero_count

    # Return "True" only if the maximum amount of significant digits was not reached
    return not count > significant_digits


def convert_period_to_frequency(period: float, input_unit: str = "ns", output_unit: str = "MHz"):
    pass


def convert_frequency_to_period(frequency: float, input_unit: str = "MHz", output_unit: str = "ns"):
    pass
