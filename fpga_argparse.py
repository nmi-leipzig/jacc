"""
This module contaisn all the necessary arg parsing of jacc.
"""
import argparse
from fpga_model import FPGAModel
from fpga_primitives import ClockBlockConfiguration
import sys

arg_meta_information = [
    {
        "short_flag": "-h",
        "flag": "--help",
        "help": "Shows this help message and exit"
    },
    {
        "short_flag": "-sm",
        "flag": "--show_models",
        "help": "Shows all supported fpga models and exit"
    },
    {
        "short_flag": "-re",
        "flag": "--use_relative_error_only_for_scoring",
        "help": "Activates the use of relative errors instead absoulte errors for scoring."
    },
    {
        "short_flag": "-model",
        "flag": "--fpga_model_specification",
        "input": "<7-series model> <speed grade> [<voltage>]",
        "help": "Specifies the used fpga model"
    },
    {
        "short_flag": "-cmtb",
        "flag": "--cmt_block",
        "input": "{mmcm, pll, MMCM, PLL}",
        "help": "Specifies the desired clock management tile block."
    },
    {
        "short_flag": "-fin1",
        "flag": "--input_frequency_1",
        "input": "<clkin1_period>",
        "help": "Specifies frequency of the input clock 1 for the CMT block.\n"
                "\tNote: The boundaries of this value depend on the selected CMT block"
    },
    {
        "short_flag": "-fout<0-6>",
        "flag": "--output_frequency_<0-6>",
        "input": "<output frequency>",
        "help": "Specifies desired frequency for the output clock <1-7>.\n"
                "\tNote: The boundaries of this value depend on the selected fpga model\n"
                "\tNote': Only the MMCM block supports an output clock 6"
    },
    {
        "short_flag": "-fdelta<0-6>",
        "flag": "--frequency_delta_<0-6>",
        "input": "<output frequency delta value>",
        "help": "Specifies the highest allowed relative error between desired fout<0-6> and actual fout<0-6>.\n"
                "\tNote: Only values > 0 are allowed.\n"
                "\tE.g: 0.5 allows an error of up to 50% of the desired value."

    },
    {
        "short_flag": "-ps<0-6>",
        "flag": "--phase_shift_<0-6>",
        "input": "<phase shift>",
        "help": "Specifies desired phase shift for the output clock <1-7> in degree.\n"
                "\tValues from -360 to 360 are possible."
    },
    {
        "short_flag": "-psdelta<0-6>",
        "flag": "--phase_shift_delta_<0-6>",
        "input": "<phase shift delta value>",
        "help": "Specifies the highest allowed relative error between desired ps<0-6> and actual phase shift.\n"
                "\tNote: Only values > 0 are allowed.\n"
                "\tE.g: 0.5 allows an error of up to 50% of the desired value."
    },
    {
        "short_flag": "-sw",
        "flag": "--startup_wait",
        "help": "Makes the CMT block wait until its start-up cycle is over."
    },
    {
        "short_flag": "-clk4c",
        "flag": "--clock_4_cascade",
        "help": "Allows the script to cascade the divider of clock 6 into clock 4.\n"
                "\tThough the script will only use the option if beneficial.\n"
                "\tNote': Only the MMCM block supports this feature."
    },
    {
        "short_flag": "-band",
        "flag": "--bandwidth",
        "input": "{HIGH, LOW, OPTIMIZED, high, low, optimized}",
        "help": "Specifies algorithm that is used by the CMT block that affects jitter, phase margin and more."
    },
    {
        "short_flag": "-rj1",
        "flag": "--ref_jitter1",
        "input": "<reference jitter>",
        "help": "Specifies the expected jitter on the input clock in unit interval (UI)\n"
                "\tNOTE: For simulation purposes (with Vivado) ONLY.\n"
                "\tValues from 0.000 to 0.999 allowed"
    },
    {
        "short_flag": "-q",
        "flag": "--quiet",
        "help": "Stops the script from printing the computed configuration into the terminal"
    },
    {
        "short_flag": "-f",
        "flag": "--file",
        "input": "<file name>",
        "help": "Writes computed configuration (if one was found) into the named file."
    },
    {
        "short_flag": "-m",
        "flag": "--module",
        "help": "Output (console and/or file) will be in form of a generated verilog module."
    },
]


def get_base_arg_parser(fpga_models: dict, program_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    # I couldn't make the example usage strings of the arguments
    # the way i wanted them to be with the default help string.
    # So I wrote them myself using a dict and a function.
    # Remember if you add new arguments to the script, you also have to add them to fpga_globals.arg_meta_information
    help_string = generate_help_string(arg_meta_information, program_name)
    parser.print_help = lambda: print(help_string)
    # Muting usage string because autogenerated usage str is confusing (wrong notations)
    parser.print_usage = lambda x: print("")

    # Argument that lets you display the list off models if chosen
    parser.add_argument("-sm", "--show_models", action="store_true")

    # Argument that lets you enter technical specifications about your fpga model
    # A custom action Class is used for this argument
    parser.add_argument("-model", "--fpga_model_specification", nargs="+", default=("artix-7", "3", "1.0V"),
                        action=verify_technical_specification(fpga_models)
                        )

    # Argument that allows choice between PLL and MMCM
    parser.add_argument("-cmtb", "--cmt_block", type=str, choices=["mmcm", "pll", "MMCM", "PLL"], default="MMCM")

    # Optional Argument for configuration score
    parser.add_argument("-re", "--use_relative_error_only_for_scoring", action="store_true")

    # Argument that mutes console output
    parser.add_argument("-q", "--quiet", action="store_true")

    # Argument specifies file output
    parser.add_argument("-f", "--file", type=str, default=False)

    # Turns the output into a verilog module
    parser.add_argument("-m", "--module", action="store_true")

    return parser


def get_configuration_arg_parser(parent: argparse.ArgumentParser, fpga_model: FPGAModel, cmt_block: ClockBlockConfiguration,
                                 ) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, parents=[parent])

    # Muting usage string because autogenerated usage str is confusing (wrong notations)
    parser.print_usage = lambda x: print("")

    # Argument sets the clkin period, this will internally be converted into a frequency
    # A custom action Class is used for this argument
    parser.add_argument("-fin1", "--input_frequency_1", type=float, dest="f_in_1", nargs="?",
                        default=10,
                        action=verify_range(
                            fpga_model.get_f_in_min(cmt_block.specification),
                            fpga_model.get_f_in_max(cmt_block.specification),
                            specification=f"{cmt_block.specification.upper()} and {fpga_model.get_identifier()}",
                                            )
                        )

    # Boolean args for startup_wait
    parser.add_argument("-sw", "--startup_wait", action="store_true")

    parser.add_argument("-band", "--bandwidth", type=str,
                        choices=["HIGH", "LOW", "OPTIMIZED", "high", "low", "optimized"])

    # A custom action Class is used for this argument
    parser.add_argument("-rj1", "--ref_jitter1", type=float, action=verify_range(cmt_block.ref_jitter1.start,
                                                                                cmt_block.ref_jitter1.end)
                        )
    if cmt_block.specification == "mmcm":
        # Argument that allows the script to use the cascade option (if beneficial)
        parser.add_argument("-clk4c", "--clock_4_cascade", action="store_true", dest="f_out_4_cascade")

    # Arguments that are available for multiple indexes use this loop:
    for index in range(cmt_block.output_clocks):
        frequency_default = 133.7 if index == 0 else None
        # Frequency argument per output clk
        parser.add_argument(f"-fout{index}", f"--output_frequency_{index}", type=float, dest=f"f_out_{index}",
                            default=frequency_default,
                            action=verify_range(fpga_model.get_f_out_min(cmt_block.specification),
                                                fpga_model.get_f_out_max(cmt_block.specification),
                                                specification=str(fpga_model.get_identifier())
                                                )
                            )

        # Delta value for frequency per output clock
        parser.add_argument(f"-fdelta{index}", f"--frequency_delta_{index}", type=float, action=verify_range(0, "+"))

        # Phase shift argument per output clock
        parser.add_argument(f"-ps{index}", f"-phase_shift_{index}", type=float, action=verify_range(-360, 360))

        # Delta value for phase shift per output clock
        parser.add_argument(f"-psdelta{index}", f"--phase_shift_delta_{index}", type=float, action=verify_range(0, "+"))

    return parser


def generate_help_string(arg_meta_information: list, program_name: str) -> str:
    usage_str = f"\nUsage: {program_name} [options]\n\n"

    # Format Optional arguments:
    optional_arguments_str = "\n\n".join([
        meta_info["short_flag"]
        + ", "
        + meta_info["flag"]
        + (("  " + meta_info["input"]) if "input" in meta_info else "")
        + "\n\t" + meta_info["help"]
        for meta_info in arg_meta_information]
    )

    return usage_str + optional_arguments_str


# Code modeled after: https://stackoverflow.com/a/4195302
def verify_technical_specification(fpga_models: dict) -> argparse.Action:
    """
    Some function that verifies the integrity of a fpga model specified by the user
    Code modeled after: https://stackoverflow.com/a/4195302
    :param fpga_models: Dictionary of all supported fpga models
    :return: ModelVerifier
    """
    class ModelVerifier(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            length = len(values)
            if not 2 <= length <= 3:
                print("Wrong number of arguments for \"--fpga_model_specification\".\n"
                      "Number of arguments needed: 2-3\n"
                      f"Number of arguments given: {length}")
                sys.exit(1)
            elif tuple(values) not in fpga_models.keys():
                msg1 = f"The fpga model with following specification is not available:\n\n" \
                       f"\t7-series model: {values[0]}\n" \
                       f"\tspeed grade: {values[1]}\n"
                if len(values) == 3:
                    msg2 = f"\tvoltage: {values[2]}\n"
                else:
                    msg2 = ""
                msg3 = "\nUse the optional argument \"--show_models\" to display all models available\n" + \
                       "FPGA Models have to entered as strings and different arguments like this:\n" \
                       "\t-model \"artix-7\" \"3\" \"1.0V\""
                print(msg1 + msg2 + msg3)
                sys.exit(1)
            else:
                setattr(args, self.dest, tuple(values))
    return ModelVerifier


# Code modeled after: https://stackoverflow.com/a/4195302
def verify_range(start: float, end: float, specification: str = None) -> argparse.Action:
    class RangeVerifier(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if values is None:
                print(f"error: argument {self.dest}: expected at least one argument.")
                sys.exit(1)
            if float(values) < start or (end != "+" and float(values) > end):
                if specification is not None:
                    string_part = f" allowed with {specification} in usage."
                else:
                    string_part = ""
                print(f"Invalid value: {values} for argument: {self.dest}.\n"
                      f"Only values in [{start}; {end}] for {self.dest}{string_part}")
                sys.exit(1)
            else:
                setattr(args, self.dest, values)
    return RangeVerifier
