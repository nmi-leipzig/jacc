


set outputDir ./output_dir/
file mkdir $outputDir

# Set the used FPGA model
set_part xc7a35ticsg324-1L



create_project -in_memory




create_ip -name clk_wiz -version 6.0 -vendor xilinx.com -module_name gunther

#report_property [get_ips gunther]
set_property CONFIG.PRIMITIVE PLL [get_ips gunther]
set_property CONFIG.PLL_CLKIN_PERIOD 1000 [get_ips gunther]



report_property [get_ips gunther]


generate_target synthesis [get_ips gunther]

