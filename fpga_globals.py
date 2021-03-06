"""
This module contains global values that are used by other modules of jacc.
Most of these are here because of separation of concerns.
They would pollute other modules by making them less readable, if they were defined at other places.
"""
from fpga_clk_attr import *
import pathlib, os
from fpga_model import FPGAModel


FPGA_MODEL_JSON_PATHS = [
    pathlib.Path(__file__).parent.joinpath("fpga_models", model)
    for model in [
        file_name for file_name
        in os.listdir(os.path.dirname(__file__) + "/fpga_models")
        if file_name.endswith(".json")
    ]
]

FPGA_MODELS = {identifier: model
               for model in [FPGAModel.from_json(path)
                             for path in FPGA_MODEL_JSON_PATHS]
               for identifier in model.get_identifier()}


def get_clock_attributes(clock_primitive: str):
    clock_attributes_pll_and_mmcm = {
        "bandwidth": ListAttribute("BANDWIDTH", "OPTIMIZED", ".BANDWIDTH(@value@)", ["OPTIMIZED", "HIGH", "LOW"]),

        "ref_jitter1": RangeAttribute("REF_JITTER1", 0.010, ".REF_JITTER1(@value@)", 0.0, 0.999, 3),

        "startup_wait": BoolAttribute("STARTUP_WAIT", False, ".STARTUP_WAIT(@value@)"),

        "clkfbout_phase": IncrementRangeAttribute("CLKFBOUT_PHASE", 0.0, ".CLKFBOUT_PHASE(@value@)", 0.0, 360.0, 3, None),

        "clkout1_divide": OutputDivider("CLKOUT1_DIVIDE", 1, ".CLKOUT1_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout2_divide": OutputDivider("CLKOUT2_DIVIDE", 1, ".CLKOUT2_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout3_divide": OutputDivider("CLKOUT3_DIVIDE", 1, ".CLKOUT3_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout4_divide": OutputDivider("CLKOUT4_DIVIDE", 1, ".CLKOUT4_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout5_divide": OutputDivider("CLKOUT5_DIVIDE", 1, ".CLKOUT5_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout0_duty_cycle": IncrementRangeAttribute("CLKOUT0_DUTY_CYCLE", 0.5, ".CLKOUT0_DUTY_CYCLE(@value@)", 0.001,
                                                      0.999, 3, None),

        "clkout1_duty_cycle": IncrementRangeAttribute("CLKOUT1_DUTY_CYCLE", 0.5, ".CLKOUT1_DUTY_CYCLE(@value@)", 0.001,
                                                      0.999, 3, None),

        "clkout2_duty_cycle": IncrementRangeAttribute("CLKOUT2_DUTY_CYCLE", 0.5, ".CLKOUT2_DUTY_CYCLE(@value@)", 0.01,
                                                      0.999, 3, None),

        "clkout3_duty_cycle": IncrementRangeAttribute("CLKOUT3_DUTY_CYCLE", 0.5, ".CLKOUT3_DUTY_CYCLE(@value@)", 0.001,
                                                      0.999, 3, None),

        "clkout4_duty_cycle": IncrementRangeAttribute("CLKOUT4_DUTY_CYCLE", 0.5, ".CLKOUT4_DUTY_CYCLE(@value@)", 0.001,
                                                      0.999, 3, None),

        "clkout5_duty_cycle": IncrementRangeAttribute("CLKOUT5_DUTY_CYCLE", 0.5, ".CLKOUT5_DUTY_CYCLE(@value@)", 0.001,
                                                      0.999, 3, None),

        "clkout0_phase": IncrementRangeAttribute("CLKOUT0_PHASE", 0.0, ".CLKOUT0_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout1_phase": IncrementRangeAttribute("CLKOUT1_PHASE", 0.0, ".CLKOUT1_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout2_phase": IncrementRangeAttribute("CLKOUT2_PHASE", 0.0, ".CLKOUT2_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout3_phase": IncrementRangeAttribute("CLKOUT3_PHASE", 0.0, ".CLKOUT3_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout4_phase": IncrementRangeAttribute("CLKOUT4_PHASE", 0.0, ".CLKOUT4_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout5_phase": IncrementRangeAttribute("CLKOUT5_PHASE", 0.0, ".CLKOUT5_PHASE(@value@)", -360.0, 360.0, 3, None),
    }

    clock_attributes_pll = {
        "clkfbout_mult": IncrementRangeAttribute("CLKFBOUT_MULT", 5, ".CLKFBOUT_MULT(@value@)", 2, 64, 0, 1),

        "divclk_divide": IncrementRangeAttribute("DIVCLK_DIVIDE", 1, ".DIVCLK_DIVIDE(@value@)", 1, 56, 0, 1),

        "clkin1_period": RangeAttribute("CLKIN_PERIOD", 0.0, ".CLKIN1_PERIOD(@value@)", 0.0, 1000 / 19, 3),

        "clkout0_divide": OutputDivider("CLKOUT0_DIVIDE", 1, ".CLKOUT0_DIVIDE(@value@)", 1, 128, 0, 1)

    }

    clock_attributes_mmcm = {
        "clkfbout_mult_f": IncrementRangeAttribute("CLKFBOUT_MULT_F", 5.0, ".CLKFBOUT_MULT_F(@value@)", 2.0, 64.0, 3,
                                                   0.125),

        "clkin1_period": RangeAttribute("CLKIN1_PERIOD", 0.0, ".CLKIN1_PERIOD(@value@)", 0.0, 100.0, 3),

        "divclk_divide": IncrementRangeAttribute("DIVCLK_DIVIDE", 1, ".DIVCLK_DIVIDE(@value@)", 1, 106, 0, 1),

        "clkout4_cascade": BoolAttribute("CLKOUT4_CASCADE", False, ".CLKOUT4_CASCADE(@value@)"),

        "clkout6_divide": OutputDivider("CLKOUT6_DIVIDE", 1, ".CLKOUT6_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout6_duty_cycle": IncrementRangeAttribute("CLKOUT6_DUTY_CYCLE", 0.5, ".CLKOUT6_DUTY_CYCLE(@value@)", 0.001,
                                                      0.999, 3, None),

        "clkout6_phase": IncrementRangeAttribute("CLKOUT6_PHASE", 0.0, ".CLKOUT6_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout0_divide_f": OutputDivider("CLKOUT0_DIVIDE_F", 1, ".CLKOUT0_DIVIDE_F(@value@)", 2.0, 128.0, 3, 0.125,
                                          additional_values=[1])
    }

    if clock_primitive == "PllBlockConfiguration":
        return {**clock_attributes_pll_and_mmcm, **clock_attributes_pll}

    elif clock_primitive == "MmcmBlockConfiguration":
        return {**clock_attributes_pll_and_mmcm, **clock_attributes_mmcm}

    else:
        return None
