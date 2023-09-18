#@Note Read Tcl parameters
#
#@param num         Parameter number
#@default_value     Default value if there is no parameter with requested number
#@retval            Parameter value
proc read_param {num default_value} {
    if {[llength $::argv] > $num} {
        puts "Script parameter ${num} is [lindex $::argv $num]"
        return [lindex $::argv $num]
    } else {
        return ${default_value}
    }
}

#Get script path
set script_path     [file dirname [file normalize [info script]]]

#Get configuration from script parameters
set project_folder_name     [read_param 0 "create_bd"]
set board_name              [read_param 1 "mlite_7010"]

#Set configuration for known parameters
set prj_name        ${board_name}
set prj_path        [file normalize ${script_path}/../../${project_folder_name}]
set board_path      [file normalize ${script_path}/../../board/${board_name}]
set ip_repo_path    [file normalize ${script_path}/../../ip_repo]

#Aux. processes
source ${script_path}/aux_proc.tcl
source ${board_path}/platform.tcl

#Get platform configuration
set part_name [platfrom_get_part]

#Create project
create_project ${prj_name} ${prj_path} -part ${part_name} -force

#Create xcleanup.bat file
create_prj_cleanup ${prj_path} ${prj_name}

exit