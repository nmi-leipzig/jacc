from clk_attr import *


def get_clock_attributes(clock_primitive: str):
    clock_attributes_pll_and_mmcm = {
        "bandwidth": ListAttribute("BANDWIDTH", "OPTIMIZED", ["OPTIMIZED", "HIGH", "LOW"],
                                   ".BANDWIDTH(@value@)"),

        # TODO LOOK UP digits
        "ref_jitter1": SigDigitRangeAttribute("REF_JITTER1", 0.010,
                                              ".REF_JITTER1(@value@)", 0.0, 0.999, 3),

        "startup_wait": BoolAttribute("START_WAIT", False, ".STARTUP_WAIT(@value@)"),

        "clkfbout_phase": SigDigitRangeAttribute("CLKFBOUT_PHASE", 0.0,
                                                 ".CLKFBOUT_PHASE(@value@)",
                                                 -360.0, 360.0, 3),  # TODO LOOK UP digits

        "clkout1_divide": IncrementRangeAttribute("CLKOUT1_DIVIDE", 1,
                                                  ".CLKOUT1_DIVIDE(@value@)",
                                                  1, 128, 1),

        "clkout2_divide": IncrementRangeAttribute("CLKOUT2_DIVIDE", 1,
                                                  ".CLKOUT2_DIVIDE(@value@)",
                                                  1, 128, 1),

        "clkout3_divide": IncrementRangeAttribute("CLKOUT3_DIVIDE", 1,
                                                  ".CLKOUT3_DIVIDE(@value@)",
                                                  1, 128, 1),

        "clkout4_divide": IncrementRangeAttribute("CLKOUT4_DIVIDE", 1,
                                                  ".CLKOUT4_DIVIDE(@value@)",
                                                  1, 128, 1),

        "clkout5_divide": IncrementRangeAttribute("CLKOUT5_DIVIDE", 1,
                                                  ".CLKOUT5_DIVIDE(@value@)",
                                                  1, 128, 1),

        "clkout0_duty_cycle": SigDigitRangeAttribute("CLKOUT0_DUTY_CYCLE", 0.5,
                                                     ".CLKOUT0_DUTY_CYCLE(@value@)",
                                                     0.01, 0.99, 2),

        # TODO verify duty cycle significant digit
        "clkout1_duty_cycle": SigDigitRangeAttribute("CLKOUT1_DUTY_CYCLE", 0.5,
                                                     ".CLKOUT1_DUTY_CYCLE(@value@)", 0.01,
                                                     0.99, 2),

        "clkout2_duty_cycle": SigDigitRangeAttribute("CLKOUT2_DUTY_CYCLE", 0.5,
                                                     ".CLKOUT2_DUTY_CYCLE(@value@)", 0.01,
                                                     0.99, 2),

        "clkout3_duty_cycle": SigDigitRangeAttribute("CLKOUT3_DUTY_CYCLE", 0.5,
                                                     ".CLKOUT3_DUTY_CYCLE(@value@)", 0.01,
                                                     0.99, 2),

        "clkout4_duty_cycle": SigDigitRangeAttribute("CLKOUT4_DUTY_CYCLE", 0.5,
                                                     ".CLKOUT4_DUTY_CYCLE(@value@)", 0.01,
                                                     0.99, 2),

        "clkout5_duty_cycle": SigDigitRangeAttribute("CLKOUT5_DUTY_CYCLE", 0.5,
                                                     ".CLKOUT5_DUTY_CYCLE(@value@)", 0.01,
                                                     0.99, 2),

        # TODO verify phase sig digit
        "clkout0_phase": SigDigitRangeAttribute("CLKOUT0_PHASE", 0.0,
                                                ".CLKOUT0_PHASE(@value@)",
                                                -360.0, 360.0, 3),

        "clkout1_phase": SigDigitRangeAttribute("CLKOUT1_PHASE", 0.0,
                                                ".CLKOUT1_PHASE(@value@)",
                                                -360.0, 360.0, 3),

        "clkout2_phase": SigDigitRangeAttribute("CLKOUT2_PHASE", 0.0,
                                                ".CLKOUT2_PHASE(@value@)",
                                                -360.0, 360.0, 3),

        "clkout3_phase": SigDigitRangeAttribute("CLKOUT3_PHASE", 0.0,
                                                ".CLKOUT3_PHASE(@value@)",
                                                -360.0, 360.0, 3),

        "clkout4_phase": SigDigitRangeAttribute("CLKOUT4_PHASE", 0.0,
                                                ".CLKOUT4_PHASE(@value@)",
                                                -360.0, 360.0, 3),

        "clkout5_phase": SigDigitRangeAttribute("CLKOUT5_PHASE", 0.0,
                                                ".CLKOUT5_PHASE(@value@)",
                                                -360.0, 360.0, 3),
    }

    clock_attributes_pll = {
        "clkout0_divide": IncrementRangeAttribute("CLKOUT0_DIVIDE", 1,
                                                  ".CLKOUT0_DIVIDE(@value@)",
                                                  1, 128, 1),

        "clkfbout_mult": IncrementRangeAttribute("CLKFBOUT_MULT", 5, ".CLKFBOUT_MULT(@value@)",
                                                 2, 64, 1),

        "divclk_divide": IncrementRangeAttribute("DIVCLK_DIVIDE", 1, ".DIVCLK_DIVIDE(@value@)",
                                                 1, 56, 1),

        "clkin1_period": SigDigitRangeAttribute("CLKIN1_PERIOD", 0.0, ".CLKIN1_PERIOD(@value@)",
                                                0.0, 52.631, 3),  # TODO LOOK UP digits

    }

    clock_attributes_mmcm = {
        "clkout0_divide_f": IncrementRangeAttribute("CLKOUT0_DIVIDE_F", 1.0,
                                                    ".CLKOUT0_DIVIDE_F(@value@)",
                                                    1.0, 128.0, 0.125),

        "clkfbout_mult_f": IncrementRangeAttribute("CLKFBOUT_MULT_F", 5.0, ".CLKFBOUT_MULT_F(@value@)",
                                                   2.0, 64.0, 0.125),

        "clkin1_period": SigDigitRangeAttribute("CLKIN1_PERIOD", 0.0, ".CLKIN1_PERIOD(@value@)",
                                                0.0, 100.0, 3),  # TODO LOOK UP digits

        "divclk_divide": IncrementRangeAttribute("DIVCLK_DIVIDE", 1, ".DIVCLK_DIVIDE(@value@)",
                                                 1, 106, 1),

        "clkout4_cascade": BoolAttribute("CLKOUT4_CASCADE", False, ".CLKOUT4_CASCADE(@value@)"),

        "clkout6_divide": IncrementRangeAttribute("CLKOUT6_DIVIDE", 1,
                                                  ".CLKOUT6_DIVIDE(@value@)",
                                                  1, 128, 1),

        "clkout6_duty_cycle": SigDigitRangeAttribute("CLKOUT6_DUTY_CYCLE", 0.5,
                                                     ".CLKOUT6_DUTY_CYCLE(@value@)", 0.01,
                                                     0.99, 2),

        "clkout6_phase": SigDigitRangeAttribute("CLKOUT6_PHASE", 0.0,
                                                ".CLKOUT6_PHASE(@value@)",
                                                -360.0, 360.0, 3),
    }

    if clock_primitive == "Plle2Base":
        return {**clock_attributes_pll_and_mmcm, **clock_attributes_pll}

    elif clock_primitive == "Mmcme2Base":
        return {**clock_attributes_pll_and_mmcm, **clock_attributes_mmcm}

    else:
        return None
