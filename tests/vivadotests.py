import unittest
from pathlib import Path
import os
from fpgaglobals import FPGA_MODELS
from fpgaprimitives import Mmcme2Base, Plle2Base
from fpgaconfigurations import ClockingConfigurator
import subprocess

# The tests of this module can only work with the vivado binary
vivado_binary_path = "~/Xilinx/Vivado/2020.2/bin/vivado"
vivado_binary_available = Path(vivado_binary_path).is_file() and os.access(vivado_binary_path, os.X_OK)


def write_tcl_script(fpga_model_full_name: str, simulated_input_frequency: float = None, clock_report: bool = False,
                     integrity_test: bool = False, primitive: str = "PLL", properties: dict = dict()):
    with open("tests/tcl/generated_test_script.tcl", "w") as file:
        if clock_report:
            file.write("set outputDir ./tests/tcl/output_dir\n"
                       f"set_part {fpga_model_full_name}\n"
                       "read_verilog ./tests/tcl/generated_test_template.v\n"
                       "synth_design -top clk\n"
                       f"create_clock -name simulated_in_clk -period {round((1 / simulated_input_frequency) * 1000, 3)}"
                       " [get_ports clkin1]\n"
                       "opt_design\n"
                       "power_opt_design\n"
                       "place_design\n"
                       "phys_opt_design\n"
                       "route_design\n"
                       "report_clocks -file $outputDir/generated_test_clock_report.rpt\n"
                       "#write_bitstream $outputDir/design.bit\n")

        if integrity_test:
            file.write("set outputDir ./tests/tcl/output_dir\n"
                       "create_project -in_memory\n"
                       f"set_part {fpga_model_full_name}\n"
                       "create_ip -name clk_wiz -version 6.0 -vendor xilinx.com -module_name clk_wiz_instance\n"
                       "report_property [get_ips clk_wiz_instance]\n"
                       f"set_property CONFIG.PRIMITIVE {primitive} [get_ips clk_wiz_instance]\n")
            for key, value in properties.items():
                file.write(f"set_property CONFIG.{primitive}_{key} {value} [get_ips clk_wiz_instance]\n")


def write_test_verilog_template(template: str):
    with open(Path(__file__).parent.joinpath("tcl", "generated_test_template.v"), "w") as file:
        file.write(template)


def run_generated_tcl_script():
    args = (vivado_binary_path, "-mode", "batch", "-source", "tests/tcl/generated_test_script.tcl", "-journal",
            "tests/tcl/output_dir/vivado.jou", "-log", "tests/tcl/output_dir/vivado.log")
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    s = str(popen.stdout.read())
    popen.stdout.close()
    return s


def get_value_dict_from_clock_report():
    s = ""
    with open("tests/tcl/output_dir/generated_test_clock_report.rpt") as file:
        s = "".join([line for line in file.readlines()])

    return {split[0]: {
        "period": float(split[1]),
        "phase_shift": float(split[2][1:]) / float(split[1]) * 360,
        "duty_cycle": (round(float(split[3][:-1]) - float(split[2][1:])) / float(split[1]), 3)}
        for split in
        [clock_line.split() for clock_line in
         s.split("Attributes  Sources")[1].split("====================================================")[0].split("\n")
         if clock_line != ""]
    }


@unittest.skipIf(not vivado_binary_available, "Gunther")
class VivadoTest(unittest.TestCase):

    def setUp(self) -> None:
        self.artix_mmcm_base_configuration = ClockingConfigurator(FPGA_MODELS[("artix-7", "-1", "1.0V")], Mmcme2Base.get_new_instance())
        self.artix_pll_base_configuration = ClockingConfigurator(FPGA_MODELS[("artix-7", "-1", "1.0V")], Plle2Base.get_new_instance())

    def test_artix_mmcm(self):
        desired_values_dict = {"f_in_1": 10, "f_out_0": 600, "f_out_1": 300, "delta_0": 0, "delta_1": 0}
        desired_out_count = 2
        self.artix_mmcm_base_configuration.configure_frequency_parameters(**desired_values_dict)

        # Test calculated values' integrity with clk wiz from vivado
        write_tcl_script("xc7a35ticsg324-1L", integrity_test=True, primitive="MMCM",
                         properties=self.artix_mmcm_base_configuration.get_properties_dict())
        log = run_generated_tcl_script()

        # Test if clk wiz threw no errors
        self.assertNotIn("ERROR:", log)

        write_test_verilog_template(self.artix_mmcm_base_configuration.generate_template())
        write_tcl_script("xc7a35ticsg324-1L", simulated_input_frequency=10, clock_report=True)
        log = run_generated_tcl_script()

        # Test if synthesis threw no error
        self.assertNotIn("ERROR:", log)

        # Test if values of created clocks are according to desired values
        report_dict = get_value_dict_from_clock_report()
        for key in range(desired_out_count):
            temp_delta = 1 / desired_values_dict[f"delta_{key}"] if desired_values_dict[f"delta_{key}"] != 0 else 0
            self.assertAlmostEqual(round(1 / desired_values_dict[f"f_out_{key}"], 6),
                                   report_dict[f"clkout{key}_OBUF"]["period"] / 1000,
                                   delta=temp_delta)

    def test_artix_pll(self):
        desired_values_dict = {"f_in_1": 19, "f_out_0": 600, "f_out_1": 300, "delta_0": 3, "delta_1": 3}
        desired_out_count = 2
        self.artix_pll_base_configuration.configure_frequency_parameters(**desired_values_dict)

        # Test calculated values' integrity with clk wiz from vivado
        write_tcl_script("xc7a35ticsg324-1L", integrity_test=True, primitive="PLL",
                         properties=self.artix_pll_base_configuration.get_properties_dict())
        log = run_generated_tcl_script()

        # Test if clk wiz threw no errors
        self.assertNotIn("ERROR:", log)

        write_test_verilog_template(self.artix_pll_base_configuration.generate_template())
        write_tcl_script("xc7a35ticsg324-1L", simulated_input_frequency=10, clock_report=True)
        log = run_generated_tcl_script()

        # Test if synthesis threw no error
        self.assertNotIn("ERROR:", log)

        # Test if values of created clocks are according to desired values
        report_dict = get_value_dict_from_clock_report()
        for key in range(desired_out_count):
            temp_delta = 1 / desired_values_dict[f"delta_{key}"] if desired_values_dict[f"delta_{key}"] != 0 else 0
            self.assertAlmostEqual(round(1 / desired_values_dict[f"f_out_{key}"], 6),
                                   report_dict[f"clkout{key}_OBUF"]["period"] / 1000,
                                   delta=temp_delta)
