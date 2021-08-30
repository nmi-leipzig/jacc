from clkattr import *
import pathlib
from fpgamodel import FPGAModel

FPGA_MODEL_JSON_PATHS = [pathlib.Path(__file__).parent.joinpath("fpga_models", "artix_-1_1x0v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "artix_-1LI_0x95v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "artix_-2_-2LE_1x0v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "artix_-2LE_0x9v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "artix_-3_1x0v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "dummy_fpga.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "kintex_-1_1x0v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "kintex_-1M_-1LM_-1Q_1x0v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "kintex_-2_-2LE_1x0v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "kintex_-2LE_0x9v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "kintex_-2LI_0x95v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "kintex_-3_1x0v.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "virtex_-1M.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "virtex_-1.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "virtex_-2_-2L_-2G.json"),
                         pathlib.Path(__file__).parent.joinpath("fpga_models", "virtex_-3.json")
                         ]

FPGA_MODELS = {identifier: model
               for model in [FPGAModel.from_json(path)
                             for path in FPGA_MODEL_JSON_PATHS]
               for identifier in model.get_identifier()}


def get_clock_attributes(clock_primitive: str):
    clock_attributes_pll_and_mmcm = {
        "bandwidth": ListAttribute("BANDWIDTH", "OPTIMIZED", ".BANDWIDTH(@value@)", ["OPTIMIZED", "HIGH", "LOW"]),

        # TODO LOOK UP digits
        "ref_jitter1": RangeAttribute("REF_JITTER1", 0.010, ".REF_JITTER1(@value@)", 0.0, 0.999, 3),

        "startup_wait": BoolAttribute("START_WAIT", False, ".STARTUP_WAIT(@value@)"),

        "clkfbout_phase": IncrementRangeAttribute("CLKFBOUT_PHASE", 0.0, ".CLKFBOUT_PHASE(@value@)", 0.0, 360.0, 3, None),

        "clkout1_divide": OutputDivider("CLKOUT1_DIVIDE", 1, ".CLKOUT1_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout2_divide": OutputDivider("CLKOUT2_DIVIDE", 1, ".CLKOUT2_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout3_divide": OutputDivider("CLKOUT3_DIVIDE", 1, ".CLKOUT3_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout4_divide": OutputDivider("CLKOUT4_DIVIDE", 1, ".CLKOUT4_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout5_divide": OutputDivider("CLKOUT5_DIVIDE", 1, ".CLKOUT5_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkout0_duty_cycle": IncrementRangeAttribute("CLKOUT0_DUTY_CYCLE", 0.5, ".CLKOUT0_DUTY_CYCLE(@value@)", 0.01,
                                                      0.99, 2, None),

        # TODO verify duty cycle significant digit
        "clkout1_duty_cycle": IncrementRangeAttribute("CLKOUT1_DUTY_CYCLE", 0.5, ".CLKOUT1_DUTY_CYCLE(@value@)", 0.01,
                                                      0.99, 2, None),

        "clkout2_duty_cycle": IncrementRangeAttribute("CLKOUT2_DUTY_CYCLE", 0.5, ".CLKOUT2_DUTY_CYCLE(@value@)", 0.01,
                                                      0.99, 2, None),

        "clkout3_duty_cycle": IncrementRangeAttribute("CLKOUT3_DUTY_CYCLE", 0.5, ".CLKOUT3_DUTY_CYCLE(@value@)", 0.01,
                                                      0.99, 2, None),

        "clkout4_duty_cycle": IncrementRangeAttribute("CLKOUT4_DUTY_CYCLE", 0.5, ".CLKOUT4_DUTY_CYCLE(@value@)", 0.01,
                                                      0.99, 2, None),

        "clkout5_duty_cycle": IncrementRangeAttribute("CLKOUT5_DUTY_CYCLE", 0.5, ".CLKOUT5_DUTY_CYCLE(@value@)", 0.01,
                                                      0.99, 2, None),

        # TODO verify phase sig digit
        "clkout0_phase": IncrementRangeAttribute("CLKOUT0_PHASE", 0.0, ".CLKOUT0_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout1_phase": IncrementRangeAttribute("CLKOUT1_PHASE", 0.0, ".CLKOUT1_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout2_phase": IncrementRangeAttribute("CLKOUT2_PHASE", 0.0, ".CLKOUT2_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout3_phase": IncrementRangeAttribute("CLKOUT3_PHASE", 0.0, ".CLKOUT3_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout4_phase": IncrementRangeAttribute("CLKOUT4_PHASE", 0.0, ".CLKOUT4_PHASE(@value@)", -360.0, 360.0, 3, None),

        "clkout5_phase": IncrementRangeAttribute("CLKOUT5_PHASE", 0.0, ".CLKOUT5_PHASE(@value@)", -360.0, 360.0, 3, None),
    }

    clock_attributes_pll = {
        "clkout0_divide": OutputDivider("CLKOUT0_DIVIDE", 1, ".CLKOUT0_DIVIDE(@value@)", 1, 128, 0, 1),

        "clkfbout_mult": IncrementRangeAttribute("CLKFBOUT_MULT", 5, ".CLKFBOUT_MULT(@value@)", 2, 64, 0, 1),

        "divclk_divide": IncrementRangeAttribute("DIVCLK_DIVIDE", 1, ".DIVCLK_DIVIDE(@value@)", 1, 56, 0, 1),

        "clkin1_period": RangeAttribute("CLKIN_PERIOD", 0.0, ".CLKIN1_PERIOD(@value@)", 0.0, 52.631, 3),  # TODO LOOK UP digits

    }

    clock_attributes_mmcm = {
        "clkout0_divide_f": OutputDivider("CLKOUT0_DIVIDE_F", 1, ".CLKOUT0_DIVIDE_F(@value@)", 2.0, 128.0, 3, 0.125,
                                          additional_values=[1]),

        "clkfbout_mult_f": IncrementRangeAttribute("CLKFBOUT_MULT_F", 5.0, ".CLKFBOUT_MULT_F(@value@)", 2.0, 64.0, 3,
                                                   0.125),

        "clkin1_period": RangeAttribute("CLKIN1_PERIOD", 0.0, ".CLKIN1_PERIOD(@value@)", 0.0, 100.0, 3),  # TODO LOOK UP digits

        "divclk_divide": IncrementRangeAttribute("DIVCLK_DIVIDE", 1, ".DIVCLK_DIVIDE(@value@)", 1, 106, 1, 0),

        "clkout4_cascade": BoolAttribute("CLKOUT4_CASCADE", False, ".CLKOUT4_CASCADE(@value@)"),

        "clkout6_divide": OutputDivider("CLKOUT6_DIVIDE", 1, ".CLKOUT6_DIVIDE(@value@)", 1, 128, 1, 0),

        "clkout6_duty_cycle": IncrementRangeAttribute("CLKOUT6_DUTY_CYCLE", 0.5, ".CLKOUT6_DUTY_CYCLE(@value@)", 0.01,
                                                      0.99, 2, None),

        "clkout6_phase": IncrementRangeAttribute("CLKOUT6_PHASE", 0.0, ".CLKOUT6_PHASE(@value@)", -360.0, 360.0, 3, None),
    }

    if clock_primitive == "Plle2Base":
        return {**clock_attributes_pll_and_mmcm, **clock_attributes_pll}

    elif clock_primitive == "Mmcme2Base":
        return {**clock_attributes_pll_and_mmcm, **clock_attributes_mmcm}

    else:
        return None
