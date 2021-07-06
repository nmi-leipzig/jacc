from abc import ABC, abstractmethod
from utility import check_significant_digits
from decimal import Decimal


class ClockAttribute(ABC):

    def __init__(self, name: str, default_value, template: str):
        self.name = name
        self.default_value = default_value
        self.value = default_value
        self.template = template

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def set_value(self, value):
        pass

    def instantiate_template(self):
        return self.template.replace("@value@", str(self.value))


class RangeAttribute(ClockAttribute):

    def __init__(self, name: str, default_value, template: str, start, end):
        ClockAttribute.__init__(self, name, default_value, template)

        # Cast the range identifiers to the correct number type (in case it wasn't done already)
        self.default = default_value
        self.value = self.default

        self.start = start
        self.end = end

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def set_value(self, value):
        pass


class IncrementRangeAttribute(RangeAttribute):

    def __init__(self, name: str, default_value, template: str, start, end, increment):
        RangeAttribute.__init__(self, name, default_value, template, start, end)

        self.increment = increment

    def is_valid(self) -> bool:
        # Check if value is within range
        within_range = self.start <= self.value <= self.end
        # Check if value fits increment
        # This works for floats in this case
        # Because the increment is usually 0.125 (will not lead to false positive rounding errors)
        correct_increment = not (self.value % self.increment)

        return within_range and correct_increment

    def set_value(self, value):
        if value < self.start:
            self.value = self.start
        elif value > self.end:
            self.value = self.end
        else:
            self.value = value
        # TODO verify floating point error
        #self.value = value - (value % self.increment)

    def get_range_as_generator(self, start=None, end=None):
        current_value = self.start if start is None or start < self.start else start
        generator_end = self.end if end is None or end > self.end else end

        while current_value <= generator_end:
            yield current_value
            current_value += self.increment


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

    def set_value(self, value):
        # TODO check sig digits
        self.value = value

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