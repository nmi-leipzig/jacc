set outputDir ./tests/tcl/output_dir
set_part xc7a35ticsg324-1L
read_verilog ./tests/tcl/generated_test_template.v
synth_design -top clk
create_clock -name simulated_in_clk -period 100.0 [get_ports clkin1]
opt_design
power_opt_design
place_design
phys_opt_design
route_design
report_clocks -file $outputDir/generated_test_clock_report.rpt
#write_bitstream $outputDir/design.bit
