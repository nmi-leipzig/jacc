from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from bisect import bisect
from math import ceil, floor
from utility import relative_error


@dataclass
class ClockAttribute(ABC):
    """
    Base Class for all different Attributes that can be set in order to configure a fpga primitive
    """
    name: str
    default_value: Any
    template: str

    on = False
    value = None

    def __post_init__(self):
        self.value = self.default_value

    @abstractmethod
    def set_value(self, value):
        pass

    @abstractmethod
    def instantiate_template(self) -> str:
        pass

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value and self.on == other.on \
               and type(self) == type(other)

    def __ne__(self, other):
        return not (self.name == other.name and self.value == other.value and self.on == other.on
                    and type(self) == type(other))


@dataclass
class RangeAttribute(ClockAttribute):
    """
    Class for number Attributes whose value has to be within a specific range (like [0.0; 52.631])
    """
    start: Any
    end: Any
    decimal_places: int

    def set_value(self, value):
        # Check if value is float or int and throw error if needed
        if not (isinstance(value, int) or isinstance(value, float)):
            raise TypeError(f"Error, wrong type used. Value \"{value}\" has invalid type \"{type(value)}\"")
        if value < self.start or value > self.end:
            raise ValueError(f"Error, value \"{value}\" is invalid. Value should be within [{self.start}; {self.end}]")

        self.value = value

    def instantiate_template(self) -> str:
        return self.template.replace("@value@", f"{self.value:.{self.decimal_places}f}")


@dataclass
class IncrementRangeAttribute(RangeAttribute):
    """
    Class for Range Attributes whose value can only be incremented by a specific value, e.g. 0.125.
    It also provides a generator (get_range_as_generator) which iterates through all possible values within the range.
    """
    increment: Any

    def set_and_correct_value(self, target_value):
        """
        A value as close as possible to the target_value is set
        set_value is inherited from RangeAttribute and can therefore still be used as a shortcut if needed
        """
        # ValueError check is not needed since it will be thrown anyway if comparison of str and numbers is attempted

        # Skip everything below if the target value is out of bounds or equal to the min/max value
        if target_value <= self.start:
            self.value = self.start
            return
        elif target_value >= self.end:
            self.value = self.end
            return

        # The value can only be increased in "self.increment" steps
        # The target value is often in between two of these steps
        # These two steps (lower and upper bound) are determined here:
        factor = (target_value - self.start) / self.increment
        lower_bound = floor(factor) * self.increment + self.start
        upper_bound = ceil(factor) * self.increment + self.start
        if self.end < upper_bound:
            upper_bound = self.end

        # Chose between lower and upper bound the one that's closer to the target value
        if relative_error(target_value, lower_bound) < relative_error(target_value, upper_bound):
            self.value = lower_bound
        else:
            self.value = upper_bound

    def get_range_as_generator(self, start=None, end=None):
        """
        Generator that goes through all possible values for the instance of RangeIncrementAttribute
        """
        generator_start = self.start if start is None or start < self.start else start
        generator_end = self.end if end is None or end > self.end else end
        # Multiplication is used here because it is safer than Addition when it comes to floating point precision
        factor = 0

        while generator_start + factor * self.increment < generator_end:
            yield generator_start + factor * self.increment
            factor += 1
        yield generator_end


@dataclass
class OutputDivider(RangeAttribute):
    """
    Class specifically made for the output dividers (like CLKOUT1_DIVIDE).
    It seems very similar to IncrementRangeAttribute but it functionality is different.
    It does not use any of IncrementRangeAttributes' methods and does therefore not inherit from it.
    """
    increment: float
    # A list of values that can be set, but are not within the "range"
    # Also https://docs.python.org/3/library/dataclasses.html#dataclasses.field
    additional_values: list = field(default_factory=lambda: [])

    def set_value(self, value):
        """
        Inherited method from RangeAttribute is overwritten to a None returning method since ot should not be used by
        this class
        """
        pass

    def get_bounds_based_on_value(self, target_value):
        """
        The target_value is often between two possible values.
        These two values are called the lower and upper bound in this case.
        This method returns those two bounds as a tuple.
        The choice between the two bounds depends on external values
        and is therefore done by another class for Separation Of Concerns
        """
        # ValueError check is not needed since it will be thrown anyway if bisect of str and numbers is attempted

        # This list comprehension way is rather inefficient
        # But it looks cleaner than going through "additional_values" and values within the range separately
        possible_values = self.additional_values + [self.start + self.increment * n
                                                    for n
                                                    in range(round((self.end - self.start) / self.increment) + 1)]
        possible_values.sort()
        # Usage of the bisect method from bisect https://docs.python.org/3.7/library/bisect.html#module-bisect
        upper_bound_index = bisect(possible_values, target_value)
        if upper_bound_index == len(possible_values):
            upper_bound_index -= upper_bound_index

        # Return the lower and upper bound as a tuple.
        return possible_values[upper_bound_index - 1], possible_values[upper_bound_index]
        # What if the list only contains one element?
        # -> Should never happen in the given fpga scenario


@dataclass
class ListAttribute(ClockAttribute):
    """
    Class for Attributes whose values are limited to a specific (and small) list of predefined values.
    """
    values: list

    def set_value(self, value):
        if value not in self.values:
            raise ValueError(f"Error, value \"{value}\" is not valid. Valid values are {self.values}")

        self.value = value

    def instantiate_template(self) -> str:
        return self.template.replace("@value@", f"\"{self.value}\"")


@dataclass
class BoolAttribute(ClockAttribute):
    """
    Class for boolean Attributes.
    It may seem redundant, but it takes care of TypeErrors and the template instantiation
    """

    def set_value(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"Error, value should be of type bool. Type given was \"{type(value)}\"")

        self.value = value
        self.on = True

    def instantiate_template(self) -> str:
        if self.value:
            return self.template.replace("@value@", "TRUE")
        else:
            return self.template.replace("@value@", "FALSE")
