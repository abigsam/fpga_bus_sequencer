#Configure script #################################################################################
set verif_cnfg_add_sources      {0}

#Get current script path, use folder name as verification name
set verif_script_path   [file dirname [file normalize [info script]]]
set verif_name          [file tail ${verif_script_path}]


#Create verification/simulation ###################################################################
puts "\[SCRIPT\] Configure verification test ${verif_name}"

create_fileset -simset ${verif_name}

if {${verif_cnfg_add_sources} > {0}} {
    set_property SOURCE_SET sources_1 [get_filesets ${verif_name}]
    update_compile_order -fileset ${verif_name}
} else {
    set_property SOURCE_SET {} [get_filesets ${verif_name}]
}

#Add verification files
set files_sv    [findFilesNested ${verif_script_path}/ "*.sv"]
set files_svh   [findFilesNested ${verif_script_path}/ "*.svh"]
set files_wcfg  [findFiles ${verif_script_path}/wave/ "*.wcfg"]

vivado_add_files ${files_sv}   ${verif_name} {}
vivado_add_files ${files_svh}  ${verif_name} {}
vivado_add_files ${files_wcfg} ${verif_name} {}
update_compile_order -fileset ${verif_name}

#Configure
set_property -name {xsim.simulate.xsim.more_options} \
             -value {-testplusarg UVM_TESTNAME=adder_4_bit_basic_test -testplusarg UVM_VERBOSITY=UVM_LOW} \
             -objects [get_filesets ${verif_name}]

#End sequence
update_compile_order -fileset ${verif_name}
reset_simulation -simset ${verif_name} -mode behavioral
current_fileset -simset [ get_filesets ${verif_name} ]


#Unset all internal variables #####################################################################
unset verif_cnfg_add_sources
unset verif_script_path
unset verif_name