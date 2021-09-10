from fpga_argparse import get_base_arg_parser, get_configuration_arg_parser
from fpga_globals import FPGA_MODELS
from fpga_primitives import Plle2Base, Mmcme2Base
from fpga_configurator import ClockingConfigurator
import sys


def main():
    base_parser = get_base_arg_parser(FPGA_MODELS, "name")
    base_args, rest = base_parser.parse_known_args()

    if base_args.show_models:
        print_model_specifications()

    if base_args.cmt_block.upper() == "PLL":
        used_primitive = Plle2Base.get_new_instance()
    elif base_args.cmt_block.upper() == "MMCM":
        used_primitive = Mmcme2Base.get_new_instance()
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
    if base_args.automatic_deltas:
        configurator.configure_primitive_like_vivado(
            frequency_args=frequency_args_without_delta,
            phase_shift_args=phase_shifts,
            other_args=other_args
        )
    else:
        configurator.configure_primitive(
            frequency_args={**frequency_args_without_delta, **frequency_deltas},
            phase_shift_args={**phase_shifts, **phase_shift_deltas},
            other_args=other_args
        )

    if configurator.selected_candidate is not None:

        if base_args.module:
            string_representation = configurator.generate_template()
        else:
            string_representation = str(configurator.selected_candidate)

        if base_args.file:
            write_file(base_args.file, string_representation)

        if not base_args.quiet:
            print(string_representation)


def print_model_specifications() -> None:
    print("FPGA models with the following specifications are supported:")
    for key in FPGA_MODELS:
        print(f"\t{key}")
    sys.exit(0)


def write_file(path: str, content: str) -> None:
    with open(path, "w") as file:
        file.write(content)


def order_configuration_args_into_dict(configuration_args: dict) -> (dict, dict, dict, dict, dict):
    frequency_args_without_delta = {
        **{key: arg for key, arg in configuration_args.items() if "f_out_" in key and arg is not None},
        **{key: configuration_args[key] for key in ["f_out_4_cascade", "f_in_1"]}
    }

    frequency_deltas = {
        key[1:]: arg for key, arg in configuration_args.items()
        if "fdelta" in key and arg is not None
    }

    phase_shifts = {
        **{key: arg for key, arg in configuration_args.items() if "phase_shift_" in key and arg is not None},
    }

    phase_shift_deltas = {
        key[2:]: arg for key, arg in configuration_args.items()
        if "psdelta_" in key and arg is not None
    }

    other_args = {
        key: configuration_args[key] for key in ["startup_wait", "bandwidth", "ref_jitter1"]
        if configuration_args[key] is not None
    }

    return frequency_args_without_delta, frequency_deltas, phase_shifts, phase_shift_deltas, other_args


if __name__ == "__main__":
    main()
