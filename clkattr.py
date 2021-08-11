from abc import ABC, abstractmethod
from utility import check_significant_digits
from decimal import Decimal
from math import ceil, floor


class ClockAttribute(ABC):

    def __init__(self, name: str, default_value, template: str, on: bool = False):
        self.name = name
        self.default_value = default_value
        self.value = default_value
        self.template = template
        self.on = on

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    def instantiate_template(self):
        return self.template.replace("@value@", str(self.value))


class RangeAttribute(ClockAttribute):

    def __init__(self, name: str, default_value, template: str, start, end):
        ClockAttribute.__init__(self, name, default_value, template)

        self.default = default_value
        self.value = self.default

        self.start = start
        self.end = end

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def correct_and_set_value(self, value) -> bool:
        pass


class IncrementRangeAttribute(RangeAttribute):

    def __init__(self, name: str, default_value, template: str, start, end, increment, decimal_places: int):
        RangeAttribute.__init__(self, name, default_value, template, start, end)

        self.increment = increment

        # This Integer gives the point to which the value will be rounded
        self.decimal_places = decimal_places

    def is_valid(self) -> bool:
        # Check if value is within range
        within_range = self.start <= self.value <= self.end
        # Check if value fits increment
        # This works for floats in this case
        # Because the increment is usually 0.125 (and should therefore not lead to false positive rounding errors)
        correct_increment = not (self.value % self.increment)

        return within_range and correct_increment

    def correct_and_set_value(self, value):

        # Round the number to the correct decimal places (to in if decimal_places == 0)
        if self.decimal_places:
            value = round(value, self.decimal_places)

            # Mod with floating points is difficult, this is a cheap fix
            value = value - float(Decimal(str(value)) % Decimal(str(self.increment)))
        else:
            value = round(value)

            value = value - (value % self.increment)

        # Set value to minimum or maximum (in case it went out of bounds)
        if value < self.start:
            self.value = self.start
        elif value > self.end:
            self.value = self.end
        else:
            self.value = value

    def get_range_as_generator(self, start=None, end=None):
        current_value = self.start if start is None or start < self.start else start
        generator_end = self.end if end is None or end > self.end else end

        while current_value <= generator_end:
            yield current_value
            current_value += self.increment


class OutputDivider(IncrementRangeAttribute):

    def __init__(self, name: str, default_value, template: str, start, end, increment, decimal_places: int,
                 float_divider: bool = False):
        IncrementRangeAttribute.__init__(self, name, default_value, template, start, end, increment, decimal_places)
        self.float_divider = float_divider

    def correct_and_set_value_for_dividers(self, value, do_ceil: bool = False, do_floor: bool = False) -> bool:
        """
        Adapts the given value to the given restrictions before setting it
        :param value:
        :param do_ceil: Forces the function to round the value up
        :param do_floor: Forces the function to round the value down
        :return: True if the corrected value is greater or equal to the given value or False if it is less
        """

        decimal_places_temp = self.decimal_places
        # Very special case for the float divider
        # The float divider can have values between 2.000 and 128.000 OR just 1
        if self.float_divider and 0 <= value < 2:
            decimal_places_temp = 0

        if do_ceil and do_floor:
            raise ValueError("do_floor and do_ceil are set as True, which is not allowed")
        value_before_action = value

        # Round the number to the correct decimal places (to in if decimal_places == 0)
        if decimal_places_temp:
            if not(do_ceil or do_floor):
                value = round(value, decimal_places_temp)
            elif do_ceil:
                value = ceil(value * 10**decimal_places_temp) / 10 ** decimal_places_temp
            else:
                value = ceil(value * 10 ** decimal_places_temp) / 10 ** decimal_places_temp
            # Mod with floating points is difficult, this is a cheap fix
            # TODO zitat einfuegen
            value = value - float(Decimal(str(value)) % Decimal(str(self.increment)))
        else:
            if not(do_ceil or do_floor):
                value = max(round(value), 1)
            elif do_ceil:
                value = ceil(value)
            else:
                value = max(floor(value), 1)

            value = value - (value % self.increment)

        # Set value to minimum or maximum (in case it went out of bounds)
        if value < self.start and self.float_divider and self.value == 1:
            self.value = 1
        elif value < self.start:
            self.value = self.start
        elif value > self.end:
            self.value = self.end
        else:
            self.value = value

        if self.value >= value_before_action:
            return True
        else:
            return False


class SigDigitRangeAttribute(RangeAttribute):

    def __init__(self, name: str, default_value, template: str, start, end, significant_digits):
        RangeAttribute.__init__(self, name, default_value, template, start, end)

        self.significant_digits = significant_digits

    def is_valid(self) -> bool:
        # Check if value is within range
        within_range = self.start <= self.value <= self.end
        # Check significant digits (only for float)
        digits_correct = check_significant_digits(self.value, self.significant_digits)

        return within_range and digits_correct

    def correct_and_set_value(self, value) -> bool:
        # TODO check sig digits
        self.value = value
        return None

    def get_range_as_generator(self, start=None, end=None):
        # TODO
        pass


class ListAttribute(ClockAttribute):

    # "num_type" is still included in case it is needed
    def __init__(self, name: str, default_value, values: list, template: str, num_type=False):
        ClockAttribute.__init__(self, name, default_value, template)

        self.values = values

    def is_valid(self) -> bool:
        return self.value in self.values

    def set_value(self, value):
        self.value = value

    def instantiate_template(self):
        return self.template.replace("@value@", f"\"{self.value}\"")


class BoolAttribute(ClockAttribute):

    def __init__(self,name: str, default_vault, template: str):
        ClockAttribute.__init__(self, name, default_vault, template)

    def is_valid(self) -> bool:
        # Has to be implemented because of @abstractmethod
        return True

    def set_value(self, value):
        # Has to be implemented because of @abstractmethod
        # Feels like Java
        self.value = value

    def instantiate_template(self):
        if self.value:
            return self.template.replace("@value@", "TRUE")
        else:
            return self.template.replace("@value@", "FALSE")