from fpgaglobals import get_clock_attributes
from utility import frequency_to_period_ns_precision, period_to_frequency_mhz_precision, relative_error
from clkattr import *


@dataclass
class ClockPrimitive(ABC):
    bandwidth: ListAttribute
    ref_jitter1: IncrementRangeAttribute
    startup_wait: BoolAttribute
    clkfbout_phase: RangeAttribute

    clkout1_divide: OutputDivider
    clkout2_divide: OutputDivider
    clkout3_divide: OutputDivider
    clkout4_divide: OutputDivider
    clkout5_divide: OutputDivider

    clkout0_duty_cycle: IncrementRangeAttribute
    clkout1_duty_cycle: IncrementRangeAttribute
    clkout2_duty_cycle: IncrementRangeAttribute
    clkout3_duty_cycle: IncrementRangeAttribute
    clkout4_duty_cycle: IncrementRangeAttribute
    clkout5_duty_cycle: IncrementRangeAttribute

    clkout0_phase: RangeAttribute
    clkout1_phase: RangeAttribute
    clkout2_phase: RangeAttribute
    clkout3_phase: RangeAttribute
    clkout4_phase: RangeAttribute
    clkout5_phase: RangeAttribute

    # Those two do not really need to be initialized here.
    # It does make things clearer and removes warnings from my IDE tho
    divclk_divide = None
    clkin1_period = None

    specification = None
    m = None
    d = None
    o_list = None
    attributes = None
    output_clocks = None

    def __post_init__(self):
        # Set specification, m, d, o_list and attributes references
        self.initialize_multiplier_and_divider_references()

    @abstractmethod
    def generate_template(self) -> str:
        return ""

    def get_m_generator(self, start=None, end=None):
        return self.m.get_range_as_generator(start=start, end=end)

    def get_d_generator(self, start=None, end=None):
        return self.divclk_divide.get_range_as_generator(start=start, end=end)

    def get_output_frequency_dict(self) -> dict:
        return {index: (self.m.value * period_to_frequency_mhz_precision(self.clkin1_period.value)) /
                       (self.divclk_divide.value * out_divider.value)
                for index, out_divider in enumerate(self.o_list)
                if out_divider.on}

    @abstractmethod
    def get_properties_dict(self):
        return {}

    def get_output_frequency(self, index: int) -> float:
        if not 0 <= index < self.output_clocks:
            raise ValueError(f"Index out of range, pll does not have f_out with index {index}")
        if self.o_list[index].on:
            return self.m.value * period_to_frequency_mhz_precision(self.clkin1_period.value) / \
                   (self.divclk_divide.value * self.o_list[index].value)

    def get_output_divider(self, index) -> OutputDivider:
        if not 0 <= index < self.output_clocks:
            raise ValueError(f"Index out of range, primitive does not have output divider with index {index}")
        return self.o_list[index]

    def get_duty_cycle(self, index: int) -> IncrementRangeAttribute:
        if not 0 <= index < self.output_clocks:
            raise ValueError(f"Index out of range, primitive does not have duty cycle with index {index}")
        return getattr(self, f"clkout{index}_duty_cycle")

    def set_in_period_based_on_frequency(self, f_in_1: float, f_in_2: float = None):
        self.clkin1_period.set_and_correct_value(frequency_to_period_ns_precision(f_in_1))
        self.clkin1_period.on = True

    @abstractmethod
    def initialize_multiplier_and_divider_references(self):
        """
        Specializations of this class have to implement m, d and o's in order for "calc_approximated_o_dividers" to work
        Attributes named m, d, (and o's) for all specializations of this class would be sufficient in theory
        But those variable names alone might be misleading.
        Therefore references are set on top of non-common values like:
            Mmcme2Base.m <- Mmcme2Base.clkfbout_mult_f
            Plle2Base.m <- Plle2Base.clkfbout_mult
        These naming conventions fit the Xilinx documents but a common value in the form of m does also exist.
        """
        pass

    def calc_approximated_o_dividers(self, m, d, f_in_1, desired_output_frequencies: dict, deltas: dict,
                                     fpga_f_out_min: float, fpga_f_out_max: float):

        self.m.value = m
        self.m.on = True
        self.d.value = d
        self.d.on = True

        target_dividers = {index: divider
                           for index, divider
                           in enumerate(self.o_list)
                           if index in desired_output_frequencies}

        # Iterate through all outputs that are demanded
        for index, f_out in desired_output_frequencies.items():
            # Most of the time the divider value cannot be exactly achieved
            # So instead we have to chose between two values, one of them is greater than our desired value
            # and the other one is less.
            # They are called upper and lower bound in this case
            lower_bound, upper_bound = target_dividers[index].get_bounds_based_on_value((f_in_1 * m) / (d * f_out))

            # Get the output frequencies that would be generated by using the lower/upper bound divider
            lower_bound_result = (m * f_in_1) / (lower_bound * d)
            upper_bound_result = (m * f_in_1) / (upper_bound * d)

            # It is possible for the generated frequency to go beyond the technical limitations (fpga_f_out_min/max)
            # But at least one of them will not make the output frequency go beyond those limitations
            if lower_bound_result > fpga_f_out_max:
                # Chose upper_bound if lower_bound makes output frequency go beyond limitations
                target_dividers[index].value = upper_bound
            elif upper_bound_result < fpga_f_out_min:
                # Chose lower_bound if upper_bound makes output frequency go beyond limitations
                target_dividers[index].value = lower_bound
            else:
                # If both the lower and the upper bounds generated frequency is within limitations:
                # chose the one that has a smaller relative error
                if relative_error(f_out, upper_bound_result) > relative_error(f_out, lower_bound_result):
                    target_dividers[index].value = lower_bound
                else:
                    target_dividers[index].value = upper_bound

            # Activate the target divider
            target_dividers[index].on = True

        # All of the output dividers have been computed at this point
        # This loop checks whether or not the generated output frequencies are within the deviation margin
        # given by delta values
        actual_f_outs = self.get_output_frequency_dict()
        for index, f_out in desired_output_frequencies.items():
            if relative_error(actual_f_outs[index], f_out) > deltas[index]:
                # Return False and therefore make higher level functions reject this configuration
                return False

        return True

    @classmethod
    @abstractmethod
    def get_new_instance(cls):
        pass


@dataclass
class Plle2Base(ClockPrimitive):
    clkfbout_mult: IncrementRangeAttribute
    clkin1_period: IncrementRangeAttribute
    divclk_divide: IncrementRangeAttribute
    clkout0_divide: OutputDivider

    output_clocks = 6

    def __str__(self) -> str:
        attr_strings = [attr.instantiate_template() for attr in self.attributes if attr.on]

        return "\tPLLE2_BASE #(\n\t\t" + ",\n\t\t".join(attr_strings) + "\n\t)\n"

    def generate_template(self) -> str:
        return "`timescale 1ps/1ps" \
               "\nmodule clk" \
               "\n\t(" \
               "\n\t\tinput\tclkin1," \
               "\n\t\tinput\tpwrdwn," \
               "\n\t\tinput\trst," \
               "\n\t\tinput\tclkfbin," \
               "\n\t\toutput\tclkout0," \
               "\n\t\toutput\tclkout1," \
               "\n\t\toutput\tclkout2," \
               "\n\t\toutput\tclkout3," \
               "\n\t\toutput\tclkout4," \
               "\n\t\toutput\tclkout5," \
               "\n\t\toutput\tclkfbout," \
               "\n\t\toutput\tlocked" \
               "\n\t);" \
               "\n\n\t//Here could be your code for wires and input buffers" \
               f"\n\n{self.__str__()}" \
               "\tPLLE2_BASE_inst(" \
               "\n\t\t.CLKOUT0\t(clkout0)," \
               "\n\t\t.CLKOUT1\t(clkout1)," \
               "\n\t\t.CLKOUT2\t(clkout2)," \
               "\n\t\t.CLKOUT3\t(clkout3)," \
               "\n\t\t.CLKOUT4\t(clkout4)," \
               "\n\t\t.CLKOUT5\t(clkout5)," \
               "\n\t\t.CLKFBOUT\t(clkfbout)," \
               "\n\t\t.LOCKED\t(locked)," \
               "\n\t\t.CLKIN1\t(clkin1)," \
               "\n\t\t.PWRDWN\t(pwrdwn)," \
               "\n\t\t.RST\t(rst)," \
               "\n\t\t.CLKFBIN\t(clkfbin)" \
               "\n\t);" \
               "\n\n\t//Here could be your code for wires and output buffers" \
               "\n\nendmodule"

    def get_properties_dict(self):
        return {attr.name: attr.value for attr in self.attributes if attr.on}

    def initialize_multiplier_and_divider_references(self):
        self.specification = "pll"
        self.m = self.clkfbout_mult
        self.d = self.divclk_divide
        self.o_list = [self.clkout0_divide, self.clkout1_divide, self.clkout2_divide, self.clkout3_divide,
                       self.clkout4_divide, self.clkout5_divide]
        self.attributes = [self.bandwidth, self.clkfbout_mult, self.clkfbout_phase, self.clkin1_period,
                           self.divclk_divide, self.ref_jitter1, self.startup_wait, self.clkout0_divide,
                           self.clkout1_divide, self.clkout2_divide, self.clkout3_divide, self.clkout4_divide,
                           self.clkout5_divide, self.clkout0_duty_cycle, self.clkout1_duty_cycle,
                           self.clkout2_duty_cycle, self.clkout3_duty_cycle, self.clkout4_duty_cycle,
                           self.clkout5_duty_cycle, self.clkout0_phase, self.clkout1_phase, self.clkout2_phase,
                           self.clkout3_phase, self.clkout4_phase, self.clkout5_phase]

    @classmethod
    def get_new_instance(cls):
        return cls(**get_clock_attributes("Plle2Base"))


@dataclass
class Mmcme2Base(ClockPrimitive):
    clkfbout_mult_f: IncrementRangeAttribute
    clkin1_period: IncrementRangeAttribute
    divclk_divide: IncrementRangeAttribute
    clkout4_cascade: BoolAttribute
    clkout0_divide_f: OutputDivider

    clkout6_divide: OutputDivider
    clkout6_duty_cycle: IncrementRangeAttribute
    clkout6_phase: RangeAttribute

    output_clocks = 7

    def __str__(self):
        attr_strings = [attr.instantiate_template() for attr in self.attributes
                        if attr.on and attr.value != attr.default_value]
        return "\tMMCME2_BASE #(\n\t\t" + ",\n\t\t".join(attr_strings) + "\n\t)\n"

    def generate_template(self) -> str:
        return "`timescale 1ps/1ps" \
               "\nmodule clk" \
               "\n\t(" \
               "\n\t\tinput\tclkin1," \
               "\n\t\tinput\tpwrdwn," \
               "\n\t\tinput\trst," \
               "\n\t\tinput\tclkfbin," \
               "\n\t\toutput\tclkout0," \
               "\n\t\toutput\tclkout0b," \
               "\n\t\toutput\tclkout1," \
               "\n\t\toutput\tclkout1b," \
               "\n\t\toutput\tclkout2," \
               "\n\t\toutput\tclkout2b," \
               "\n\t\toutput\tclkout3," \
               "\n\t\toutput\tclkout3b," \
               "\n\t\toutput\tclkout4," \
               "\n\t\toutput\tclkout5," \
               "\n\t\toutput\tclkout6," \
               "\n\t\toutput\tclkfbout," \
               "\n\t\toutput\tclkboutb," \
               "\n\t\toutput\tlocked" \
               "\n\t);" \
               "\n\n\t//Here could be your code for wires and input buffers" \
               f"\n\n{self.__str__()}" \
               "\tMMCME2_BASE_inst(" \
               "\n\t\t.CLKOUT0\t(clkout0)," \
               "\n\t\t.CLKOUT0B\t(clkout0b)," \
               "\n\t\t.CLKOUT1\t(clkout1)," \
               "\n\t\t.CLKOUT1B\t(clkout1b)," \
               "\n\t\t.CLKOUT2\t(clkout2)," \
               "\n\t\t.CLKOUT2B\t(clkout2b)," \
               "\n\t\t.CLKOUT3\t(clkout3)," \
               "\n\t\t.CLKOUT3B\t(clkout3b)," \
               "\n\t\t.CLKOUT4\t(clkout4)," \
               "\n\t\t.CLKOUT5\t(clkout5)," \
               "\n\t\t.CLKOUT6\t(clkout6)," \
               "\n\t\t.CLKFBOUT\t(clkfbout)," \
               "\n\t\t.CLKFBOUTB\t(clkboutb)," \
               "\n\t\t.LOCKED\t(locked)," \
               "\n\t\t.CLKIN1\t(clkin1)," \
               "\n\t\t.PWRDWN\t(pwrdwn)," \
               "\n\t\t.RST\t(rst)," \
               "\n\t\t.CLKFBIN\t(clkfbin)" \
               "\n\t);" \
               "\n\n\t//Here could be your code for wires and output buffers" \
               "\n\nendmodule"

    def get_properties_dict(self):
        return {attr.name: attr.value for attr in self.attributes if attr.on}

    def initialize_multiplier_and_divider_references(self):
        self.specification = "mmcm"
        self.m = self.clkfbout_mult_f
        self.d = self.divclk_divide
        self.o_list = [self.clkout0_divide_f, self.clkout1_divide, self.clkout2_divide, self.clkout3_divide,
                       self.clkout4_divide, self.clkout5_divide, self.clkout6_divide]
        self.attributes = [self.bandwidth, self.ref_jitter1, self.startup_wait, self.clkfbout_mult_f,
                           self.clkfbout_phase, self.clkin1_period, self.divclk_divide, self.clkout4_cascade,
                           self.clkout0_divide_f, self.clkout1_divide, self.clkout2_divide, self.clkout3_divide,
                           self.clkout4_divide, self.clkout5_divide, self.clkout6_divide, self.clkout0_duty_cycle,
                           self.clkout1_duty_cycle, self.clkout2_duty_cycle, self.clkout3_duty_cycle,
                           self.clkout4_duty_cycle, self.clkout5_duty_cycle, self.clkout6_duty_cycle,
                           self.clkout0_phase, self.clkout1_phase, self.clkout2_phase, self.clkout3_phase,
                           self.clkout4_phase, self.clkout5_phase, self.clkout6_phase]

    @classmethod
    def get_new_instance(cls):
        return cls(**get_clock_attributes("Mmcme2Base"))
