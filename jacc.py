"""
This module contains the 'main.py' of jacc.
It is quite messy and could need an upgrade.
"""

from fpga_argparse import get_base_arg_parser, get_configuration_arg_parser
from fpga_globals import FPGA_MODELS
from fpga_primitives import PllBlockConfiguration, MmcmBlockConfiguration
from fpga_configurator import ClockingConfigurator
import sys


def main():
    base_parser = get_base_arg_parser(FPGA_MODELS, "name")
    base_args, rest = base_parser.parse_known_args()

    if base_args.show_models:
        print_model_specifications()

    if base_args.cmt_block.upper() == "PLL":
        used_primitive = PllBlockConfiguration.get_new_instance()
    elif base_args.cmt_block.upper() == "MMCM":
        used_primitive = MmcmBlockConfiguration.get_new_instance()
    else:
        # Should never happen unless theres a error in the code
        used_primitive = None

    configuration_parser = get_configuration_arg_parser(base_parser, FPGA_MODELS[base_args.fpga_model_specification],
                                                        used_primitive.get_new_instance())

    configuration_args = configuration_parser.parse_args()

    configuration_args_dict = vars(configuration_args)

    frequency_args_without_delta, frequency_deltas, phase_shifts, phase_shift_deltas, other_args \
        = order_configuration_args_into_dict(configuration_args_dict)

    configurator = ClockingConfigurator(FPGA_MODELS[base_args.fpga_model_specification], used_primitive)

    configurator.configure_primitive(
            frequency_args={**frequency_args_without_delta, **frequency_deltas},
            phase_shift_args={**phase_shifts, **phase_shift_deltas},
            other_args=other_args,
            use_relative_error=base_args.use_relative_error_only_for_scoring
    )

    if configurator.selected_candidate is not None:

        if base_args.module:
            string_representation = configurator.generate_template()
        else:
            string_representation = str(configurator.selected_candidate)

        if configuration_args_dict["file"]:
            write_file(configuration_args_dict["file"], string_representation)

        str_1 = "A configuration with the values below was found:\n\n"
        str_2 = "Verilog code of the generated configuration is below the dotted line:\n" + \
                    "......................................................................\n"

        print(
            str_1 +
             configurator.selected_candidate.get_result_presentation(
                clock_six_used="f_out_6" in frequency_args_without_delta) +
            "\n" +
            str_2 +
            string_representation
        )
    else:
        print(
            "No configuration that matches your requirements could be found.\n" + \
            "A close configuration may be found by specifying less strict delta values.\n"
        )

def print_model_specifications() -> None:
    print("FPGA models with the following specifications are supported:")
    for key in FPGA_MODELS:
        # Exclude the dummy fpga because it is for tests only
        if key != ("dummy", "dummy"):
            print(f"\t{key}")
    sys.exit(0)


def write_file(path: str, content: str) -> None:
    with open(path, "w") as file:
        file.write(content)


def order_configuration_args_into_dict(configuration_args: dict) -> (dict, dict, dict, dict, dict):
    frequency_args_without_delta = {
        **{key: arg for key, arg in configuration_args.items() if "f_out_" in key and arg is not None},
        **{key: configuration_args[key] for key in (["f_out_4_cascade", "f_in_1"]
                                                    if "f_out_4_cascade" in configuration_args else ["f_in_1"])
        }
    }

    frequency_deltas = {
        f"delta_{key[-1]}": arg for key, arg in configuration_args.items()
        if "frequency_delta" in key and arg is not None
    }

    phase_shifts = {
        **{f"phase_shift_{key[-1]}": arg for key, arg in configuration_args.items() if "ps" in key and arg is not None},
    }

    phase_shift_deltas = {
        f"delta_{key[-1]}": arg for key, arg in configuration_args.items()
        if "phase_shift_delta" in key and arg is not None
    }

    other_args = {
        key: configuration_args[key] for key in ["startup_wait", "bandwidth", "ref_jitter1"]
        if configuration_args[key] is not None
    }

    return frequency_args_without_delta, frequency_deltas, phase_shifts, phase_shift_deltas, other_args


if __name__ == "__main__":
    main()
