#Configure script #################################################################################
set verif_cnfg_add_sources      {1}
set verif_cnfg_time             {1000us}
set verif_cnfg_simulate_all     {true}


#Get current script path, use folder name as verification name
set verif_script_path   [file dirname [file normalize [info script]]]
set verif_name          [file tail ${verif_script_path}]


#Create verification/simulation ###################################################################
puts "\[SCRIPT\]: configure verification test ${verif_name}"

create_fileset -simset ${verif_name}

if {${verif_cnfg_add_sources} > {0}} {
    set_property SOURCE_SET sources_1 [get_filesets ${verif_name}]
} else {
    set_property SOURCE_SET {} [get_filesets ${verif_name}]
}
update_compile_order -fileset ${verif_name}

set files_sv   [findFiles ${verif_script_path} "*.sv"]
set files_svh  [findFiles ${verif_script_path} "*.svh"]
set files_v    [findFiles ${verif_script_path} "*.v"]
set files_mem  [findFiles ${verif_script_path} "*.mem"]
set files_wcfg [findFiles ${verif_script_path} "*.wcfg"]

vivado_add_files ${files_sv}   ${verif_name} {}
vivado_add_files ${files_svh}  ${verif_name} "Verilog Header"
vivado_add_files ${files_v}    ${verif_name} {}
vivado_add_files ${files_mem}  ${verif_name} "Memory Initialization Files"
vivado_add_files ${files_wcfg} ${verif_name} {}
update_compile_order -fileset ${verif_name}

#Configure
set_property -name {xsim.simulate.runtime} -value ${verif_cnfg_time} -objects [get_filesets ${verif_name}]
set_property -name {xsim.simulate.log_all_signals} -value ${verif_cnfg_simulate_all} -objects [get_filesets tb_basic]

#End sequence
update_compile_order -fileset ${verif_name}
reset_simulation -simset ${verif_name} -mode behavioral
current_fileset -simset [ get_filesets ${verif_name} ]


#Unset all internal variables #####################################################################
unset verif_cnfg_add_sources
unset verif_cnfg_time
unset verif_cnfg_simulate_all
unset verif_script_path
unset verif_name
unset files_sv
unset files_svh
unset files_v
unset files_mem