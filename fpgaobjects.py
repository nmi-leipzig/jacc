from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from fpga_globals import get_clock_attributes


class FPGAModel:
    # Declaration of attributes which are later loaded and set from xml
    # Unnecessary in theory, but in reality it helps with auto completion of the IDE
    mmcm_f_in_min = None
    mmcm_f_in_max = None
    mmcm_f_out_min = None
    mmcm_f_out_max = None
    mmcm_f_vco_min = None
    mmcm_f_vco_max = None
    mmcm_f_pfd_min = None
    mmcm_f_pfd_max = None

    pll_f_in_min = None
    pll_f_in_max = None
    pll_f_out_min = None
    pll_f_out_max = None
    pll_f_vco_min = None
    pll_f_vco_max = None
    pll_f_pfd_min = None
    pll_f_pfd_max = None

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

    def validate_pll_input_frequency(self, frequency: float):
        return self.pll_f_in_min <= frequency <= self.pll_f_in_max

    def validate_pll_out_frequency(self, frequency: float):
        return self.pll_f_out_min <= frequency <= self.pll_f_out_max

    def get_pfd_max(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_pfd_max
        elif specification == "pll":
            return self.pll_f_pfd_max
        else:
            return None

    def get_pfd_min(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_pfd_min
        elif specification == "pll":
            return self.pll_f_pfd_min
        else:
            return None

    def get_vco_max(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_vco_max
        elif specification == "pll":
            return self.pll_f_vco_max
        else:
            return None

    def get_vco_min(self, specification: str):
        if specification == "mmcm":
            return self.mmcm_f_vco_min
        elif specification == "pll":
            return self.pll_f_vco_min
        else:
            return None


class ClockPrimitive(ABC):

    def __init__(self, specification: str):
        self.specification = specification

    @abstractmethod
    def generate_template(self) -> str:
        return ""

    @abstractmethod
    def get_output_clk_count(self) -> int:
        return 0

    @abstractmethod
    def get_m_generator(self, start=None, end=None):
        return None

    @abstractmethod
    def get_d_generator(self, start=None, end=None):
        return None

    @classmethod
    @abstractmethod
    def calc_approximated_o_dividers(cls, m, d, f_in_1, desired_output_frequencies: dict, deviation: float):
        return {}


class Plle2Base(ClockPrimitive):

    def __init__(self):
        ClockPrimitive.__init__(self, "pll")

        temp_dict = get_clock_attributes("Plle2Base")

        # Set generated ClockAttribute objects as attributes
        self.bandwidth = temp_dict["bandwidth"]
        self.clkfbout_mult = temp_dict["clkfbout_mult"]
        self.clkfbout_phase = temp_dict["clkfbout_phase"]
        self.clkin1_period = temp_dict["clkin1_period"]
        self.divclk_divide = temp_dict["divclk_divide"]
        self.ref_jitter1 = temp_dict["ref_jitter1"]
        self.startup_wait = temp_dict["startup_wait"]
        self.clkout0_divide = temp_dict["clkout0_divide"]
        self.clkout1_divide = temp_dict["clkout1_divide"]
        self.clkout2_divide = temp_dict["clkout2_divide"]
        self.clkout3_divide = temp_dict["clkout3_divide"]
        self.clkout4_divide = temp_dict["clkout4_divide"]
        self.clkout5_divide = temp_dict["clkout5_divide"]
        self.clkout0_duty_cycle = temp_dict["clkout0_duty_cycle"]
        self.clkout1_duty_cycle = temp_dict["clkout1_duty_cycle"]
        self.clkout2_duty_cycle = temp_dict["clkout2_duty_cycle"]
        self.clkout3_duty_cycle = temp_dict["clkout3_duty_cycle"]
        self.clkout4_duty_cycle = temp_dict["clkout4_duty_cycle"]
        self.clkout5_duty_cycle = temp_dict["clkout5_duty_cycle"]
        self.clkout0_phase = temp_dict["clkout0_phase"]
        self.clkout1_phase = temp_dict["clkout1_phase"]
        self.clkout2_phase = temp_dict["clkout2_phase"]
        self.clkout3_phase = temp_dict["clkout3_phase"]
        self.clkout4_phase = temp_dict["clkout4_phase"]
        self.clkout5_phase = temp_dict["clkout5_phase"]

    def generate_template(self) -> str:
        attr_strings = [attr.instantiate_template() for attr in [self.bandwidth,
                                                                 self.clkfbout_mult,
                                                                 self.clkfbout_phase,
                                                                 self.clkin1_period,
                                                                 self.divclk_divide,
                                                                 self.ref_jitter1,
                                                                 self.startup_wait,
                                                                 self.clkout0_divide,
                                                                 self.clkout1_divide,
                                                                 self.clkout2_divide,
                                                                 self.clkout3_divide,
                                                                 self.clkout4_divide,
                                                                 self.clkout5_divide,
                                                                 self.clkout0_duty_cycle,
                                                                 self.clkout1_duty_cycle,
                                                                 self.clkout2_duty_cycle,
                                                                 self.clkout3_duty_cycle,
                                                                 self.clkout4_duty_cycle,
                                                                 self.clkout5_duty_cycle,
                                                                 self.clkout0_phase,
                                                                 self.clkout1_phase,
                                                                 self.clkout2_phase,
                                                                 self.clkout3_phase,
                                                                 self.clkout4_phase,
                                                                 self.clkout5_phase]]

        return "PLLE2_BASE# (" + ",\n".join(attr_strings) + ")"

    def get_output_clk_count(self) -> int:
        return 6

    def get_m_generator(self, start=None, end=None):
        return self.clkfbout_mult.get_range_as_generator(start=start, end=end)

    def get_d_generator(self, start=None, end=None):
        return self.divclk_divide.get_range_as_generator(start=start, end=end)

    def get_clkout_divide_list(self):
        # Puts all the dividers into a correctly indexed list
        return [self.clkout0_divide, self.clkout1_divide, self.clkout2_divide, self.clkout3_divide, self.clkout4_divide,
                self.clkout5_divide]

    @classmethod
    def calc_approximated_o_dividers(cls, m, d, f_in_1, desired_output_frequencies: dict, deviation: float):
        new_plle_2_base = cls()

        targeted_dividers = {index: divider
                             for index, divider
                             in enumerate(new_plle_2_base.get_clkout_divide_list())
                             if index in desired_output_frequencies}

        for index, f_out in desired_output_frequencies.items():
            targeted_dividers[index].set_value(round((f_in_1 * m) / (d * f_out)))
            actual_f_out = (f_in_1 * m) / (targeted_dividers[index].value * d)

            if actual_f_out > f_out + deviation or actual_f_out < f_out - deviation:
                return None

            print(f"{actual_f_out},  {f_out}, {m}, {d}, ")

        #print(new_plle_2_base.clkout0_divide.value)
        new_plle_2_base.clkfbout_mult.set_value(m)
        new_plle_2_base.divclk_divide.set_value(d)
        print(new_plle_2_base.generate_template())
        return new_plle_2_base


class Mmcme2Base(ClockPrimitive):

    def __init__(self):
        ClockPrimitive.__init__(self, "mmcm")

        temp_dict = get_clock_attributes("Mmcm2Base")

        self.bandwidth = temp_dict["bandwidth"]
        self.ref_jitter1 = temp_dict["ref_jitter1"]
        self.startup_wait = temp_dict["startup_wait"]
        self.clkfbout_mult_f = temp_dict["clkfbout_mult_f"]
        self.clkin1_period = temp_dict["clkin1_period"]
        self.divclk_divide = temp_dict["divclk_divide"]
        self.clkfbout_phase = temp_dict["clkfbout_phase"]
        self.clkout4_cascade = temp_dict["clkout4_cascade"]
        self.clkout0_divide_f = temp_dict["clkout0_divide_f"]
        self.clkout1_divide = temp_dict["clkout1_divide"]
        self.clkout2_divide = temp_dict["clkout2_divide"]
        self.clkout3_divide = temp_dict["clkout3_divide"]
        self.clkout4_divide = temp_dict["clkout4_divide"]
        self.clkout5_divide = temp_dict["clkout5_divide"]
        self.clkout6_divide = temp_dict["clkout6_divide"]
        self.clkout0_duty_cycle = temp_dict["clkout0_duty_cycle"]
        self.clkout1_duty_cycle = temp_dict["clkout1_duty_cycle"]
        self.clkout2_duty_cycle = temp_dict["clkout2_duty_cycle"]
        self.clkout3_duty_cycle = temp_dict["clkout3_duty_cycle"]
        self.clkout4_duty_cycle = temp_dict["clkout4_duty_cycle"]
        self.clkout5_duty_cycle = temp_dict["clkout5_duty_cycle"]
        self.clkout6_duty_cycle = temp_dict["clkout6_duty_cycle"]
        self.clkout0_phase = temp_dict["clkout0_phase"]
        self.clkout1_phase = temp_dict["clkout1_phase"]
        self.clkout2_phase = temp_dict["clkout2_phase"]
        self.clkout3_phase = temp_dict["clkout3_phase"]
        self.clkout4_phase = temp_dict["clkout4_phase"]
        self.clkout5_phase = temp_dict["clkout5_phase"]
        self.clkout6_phase = temp_dict["clkout6_phase"]

    def generate_template(self):
        attr_strings = [attr.instantiate_template() for attr in [self.bandwidth,
                                                                 self.ref_jitter1,
                                                                 self.startup_wait,
                                                                 self.clkfbout_mult_f,
                                                                 self.clkfbout_phase,
                                                                 self.clkin1_period,
                                                                 self.divclk_divide,
                                                                 self.clkout4_cascade,
                                                                 self.clkout0_divide_f,
                                                                 self.clkout1_divide,
                                                                 self.clkout2_divide,
                                                                 self.clkout3_divide,
                                                                 self.clkout4_divide,
                                                                 self.clkout5_divide,
                                                                 self.clkout6_divide,
                                                                 self.clkout0_duty_cycle,
                                                                 self.clkout1_duty_cycle,
                                                                 self.clkout2_duty_cycle,
                                                                 self.clkout3_duty_cycle,
                                                                 self.clkout4_duty_cycle,
                                                                 self.clkout5_duty_cycle,
                                                                 self.clkout6_duty_cycle,
                                                                 self.clkout0_phase,
                                                                 self.clkout1_phase,
                                                                 self.clkout2_phase,
                                                                 self.clkout3_phase,
                                                                 self.clkout4_phase,
                                                                 self.clkout5_phase,
                                                                 self.clkout6_phase]]
        return "MMCME2_BASE# (" + ",\n".join(attr_strings) + ")"
