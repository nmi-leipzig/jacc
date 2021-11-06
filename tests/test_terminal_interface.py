"""
Tests for the user/terminal interface
"""
import unittest
from pathlib import Path
import subprocess
from itertools import chain, combinations
from fpga_globals import FPGA_MODELS


def run_script_with_args(args: list) -> (str, int):
    """
    :return: The terminal output created by the script
    """
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    s = str(popen.stdout.read())
    popen.stdout.close()
    return s, popen.returncode


class TerminalInterfaceTest(unittest.TestCase):
    bool_args = ["-h", "--help", "-sm", "--show_models", "-sw", "--startup_wait",
                 "-clk4c", "--clock_4_cascade", "-q", "--quiet", "-m", "--module"]
    cmt_blocks = ["pll", "mmcm", "PLL", "MMCM"]
    fpga_specifications = [("virtex-7", "3"), ("kintex-7", "1LM", "1.0V"), ("artix-7", "2LE", "0.9V")]
    fpgas = [FPGA_MODELS[key] for key in fpga_specifications]
    fpga_out_boundaries_mmcm_f = [(fpga.get_f_out_min("mmcm"), fpga.get_f_out_max("mmcm")) for fpga in fpgas]
    fpga_out_boundaries_pll_f = [(fpga.get_f_out_min("pll"), fpga.get_f_out_max("pll")) for fpga in fpgas]
    fpga_in_boundaries_mmcm_f = [(fpga.get_f_in_min("mmcm"), fpga.get_f_in_max("mmcm")) for fpga in fpgas]
    fpga_in_boundaries_pll_f = [(fpga.get_f_in_min("pll"), fpga.get_f_in_max("pll")) for fpga in fpgas]

    def setUp(self) -> None:
        self.args = ["python", "jacc.py"]

    def test_bool_args(self):
        for arg in self.bool_args:

            output, code = run_script_with_args(self.args + [arg])
            self.assertEqual(code, 0)

    def test_frequency_boundaries_pll(self):
        for fpga, in_boundaries, out_boundaries \
                in zip(self.fpga_specifications, self.fpga_in_boundaries_pll_f, self.fpga_out_boundaries_pll_f):
            args_combinations = [
                [
                    "-fin1", in_value, "-fout0", out_boundaries[0], "-fout1", out_boundaries[1],
                    "-fout5", out_boundaries[1] / 2
                ]
                + ["-model"] + [specification_part for specification_part in fpga]
                for in_value in list(in_boundaries) + [in_boundaries[1] / 2]
            ]
            args_combinations = [[str(arg) for arg in args] for args in args_combinations]

            for args in args_combinations:
                s, code = run_script_with_args(self.args + args)
                self.assertEqual(code, 0)

    def test_frequency_boundaries_mmcm(self):
        for fpga, in_boundaries, out_boundaries \
                in zip(self.fpga_specifications, self.fpga_in_boundaries_mmcm_f, self.fpga_out_boundaries_mmcm_f):
            args_combinations = [
                [
                    "--input_frequency_1", in_value, "--output_frequency_0", out_boundaries[0],
                    "--output_frequency_1", out_boundaries[1], "--output_frequency_5", out_boundaries[1] / 2
                ]
                + ["--fpga_model_specification"] + [specification_part for specification_part in fpga]
                for in_value in list(in_boundaries) + [in_boundaries[1] / 2]
            ]
            args_combinations = [[str(arg) for arg in args] for args in args_combinations]

            for args in args_combinations:
                s, code = run_script_with_args(self.args + args)
                self.assertEqual(code, 0)

    def test_invalid_values(self):

        # Invalid fpga_model
        faulty_args_1 = [["-model", "gunther"], ["-model", "kintex-7", "5"], ["-model"],
                         ["-model", "kintex-7", "3", "True"], ["-model", "kintex-7", "3", "1.0V", "peter"]]

        # Invalid cmt block
        faulty_args_2 = [["-cmtb", "gunther"], ["-cmtb", "-3"], ["-cmtb", "-model", "kintex-7", "3", "1.0V"],
                         ["-cmtb"], ["-cmt", "True"], ["-cmt", "13.37"]]

        # Invalid input frequency
        faulty_args_3 = [["-fin1", "-1.0"], ["-fin1", "0"], ["-fin1"], ["-fin1", "Olaf"], ["-fin1", "True"],
                         ["-fin1", "int(True) + 100"], ["-fin1", "200000"]]

        # Invalid output frequency
        faulty_args_4 = [["-fout1"], ["-fout1", "Otto"], ["-fout1", "-300"], ["-fout1", "300", "-150"],
                         ["-fout1", "False"], ["-fout1", "200", "fout2", "Peter"],
                         ["-fout1", "400", "-fout2", "500", "-fout3", "500", "-fout0", "450", "-fout5", "Gustav"]]

        # Try to use features for PLL that are mmcm exclusive:
        fault_args_5 = [["-cmtb", "pll", "-clk4c"], ["-cmtb", "pll", "-ps6"], ["-cmtb", "pll", "-ps6", "100"],
                        ["-cmtb", "pll", "-fout6", "200"], ["-cmtb", "pll", "-fdelta6", "0.5"],
                        ["-cmtb", "pll", "-psdelta6", "0.3"]]

        for faulty_arg_list in [faulty_args_1, faulty_args_2, faulty_args_3, faulty_args_4, fault_args_5]:
            for args in faulty_arg_list:
                s, code = run_script_with_args(self.args + args)
                self.assertNotEqual(code, 0, msg=f"args: {args}\n script output: {s}")
