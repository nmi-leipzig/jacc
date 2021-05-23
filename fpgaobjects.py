from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
import sys
from pydoc import locate
from utility import check_significant_digits


class FPGAModel:

    def __init__(self, name: str, speed_grade: str):
        self.name = name
        self.speed_grade = speed_grade

    @classmethod
    def from_xml(cls, xml_string):
        xml_root = ET.fromstring(xml_string)
        # "name" and "speed_grade" should ALWAYS be part of the model xml and are therefore xml attributes
        fpga_model = cls(**xml_root.attrib)

        # Other attributes are read from xml elements:
        for child in xml_root:
            setattr(fpga_model, child.tag, float(child.text))

        return fpga_model

    def validate_mmcm_input_frequency(self, frequency: float):
        return self.mmcm_f_in_min <= frequency <= self.mmcm_f_in_max

    def validate_mmcm_out_frequency(self, frequency: float):
        return self.mmcm_f_out_min <= frequency <= self.mmcm_f_out_max

    def validate_mmcm_vco(self, frequency: float):
        return self.mmcm_f_vco_min <= frequency <= self.mmcm_f_vco_max

    def validate_mmcm_pfd(self, frequency: float):
        return self.mmcm_f_pfd_min <= frequency <= self.mmcm_f_pfd_max

    def validate_pll_input_frequency(self, frequency: float):
        return self.pll_f_in_min <= frequency <= self.pll_f_in_max

    def validate_pll_out_frequency(self, frequency: float):
        return self.pll_f_out_min <= frequency <= self.pll_f_out_max

    def validate_pll_vco(self, frequency: float):
        return self.pll_f_vco_min <= frequency <= self.pll_f_vco_max

    def validate_pll_pfd(self, frequency: float):
        return self.pll_f_pfd_min <= frequency <= self.pll_f_pfd_max


class PrimitiveAttribute(ABC):

    def __init__(self, name: str, default):
        self.name = name
        self.default = default
        self.value = default

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def set_value(self, value):
        pass

    # This reads and instantiates a subclass object (of PrimitiveAttribute) based on a xml_string
    @classmethod
    @abstractmethod
    def from_xml(cls, xml_string: str):
        xml_root = ET.fromstring(xml_string)
        # Get the reference for "this" module
        module = sys.modules[__name__]
        # Get the reference of the target class based on a xml attribute
        target_class = getattr(module, xml_root.attrib["type"])
        # Let the subclass instantiate itself based on the xml
        return target_class.from_xml(xml_string)


class RangeAttribute(PrimitiveAttribute):

    def __init__(self, name: str, default, start, end, num_type: str, significant_digits=False):
        PrimitiveAttribute.__init__(self, name, default)

        # Ranges could be "int" or "float"
        # The correct type is read from the xml with "locate"
        self.num_type = locate(num_type)

        # Cast significant_digits (if given) to int (False will be cast to 0)
        self.significant_digits = int(significant_digits)

        # Cast the range identifiers to the correct number type (in case it wasn't done already)
        self.default = self.num_type(default)
        self.value = self.default

        self.start = self.num_type(start)
        self.end = self.num_type(end)


    def is_valid(self) -> bool:
        # Check if value is within range
        within_range = self.start <= self.value <= self.end
        # Check significant digits (only for float)
        digits_correct = True
        if self.significant_digits:
            digits_correct = check_significant_digits(self.value, self.significant_digits)

        return within_range and digits_correct


    def set_value(self, value):
        self.value = self.num_type(value)

    # Instantiates a "RangeAttribute" object from a xml string
    @classmethod
    def from_xml(cls, xml_string: str):
        xml_root = ET.fromstring(xml_string)

        # All arguments of the RangeAttribute __init__ method can be given as simple strings
        # Therefore they are read from the xml and put into a dictionary for readability
        kwargs = {child.tag: child.text for child in xml_root}

        return cls(**kwargs)


class ListAttribute(PrimitiveAttribute):

    # "num_type" is still included in case it is needed
    def __init__(self, name: str, default, values: list, num_type=False):
        PrimitiveAttribute.__init__(self, name, default)

        self.values = values

    def is_valid(self) -> bool:
        return self.value in self.values

    def set_value(self, value):
        self.value = value

    @classmethod
    def from_xml(cls, xml_string: str):
        xml_root = ET.fromstring(xml_string)

        # Assigning all elements via dictionary comprehension first
        kwargs = {child.tag: child.text for child in xml_root}

        # Reassign "values"-attribute the correct way
        kwargs["values"] = [child.text for child in xml_root.find("values")]

        return cls(**kwargs)


class Primitive(ABC):

    def __init__(self, target_fpgas: list, template: str):
        self.target_fpgas = target_fpgas
        self.template = template

    @abstractmethod
    def generate_template(self) -> str:
        return ""

    @classmethod
    def from_xml(cls, xml_string: str):
        xml_root = ET.fromstring(xml_string)
        # Get the reference for "this" module
        module = sys.modules[__name__]
        # Get the reference of the target class based on a xml attribute
        target_class = getattr(module, xml_root.attrib["type"])

        # Read attributes from xml and assign them to the primitive

        target_fpgas = [child.text for child in xml_root.find("target_fpgas")]
        template = xml_root.find("template").text
        # Instantiate the primitive
        primitive = target_class(target_fpgas, template)

        # Assign all (sub)primitive specific attributes from the xml
        for attribute in xml_root.find("attributes"):
            setattr(primitive, attribute.attrib["name"], PrimitiveAttribute.from_xml(ET.tostring(attribute,
                                                                                                 encoding="unicode")))

        return primitive


class Mmcme2Base(Primitive):

    def __init__(self, target_fpgas: list, template: str):
        Primitive.__init__(self, target_fpgas, template)

    def generate_template(self):
        pass



