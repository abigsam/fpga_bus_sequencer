

proc make_verif {verif_path} {

    set verif_config_files [findFilesNested ${verif_path} "verif_config.tcl"]

    if {${verif_config_files} != {}} {
        puts "\[SCRIPT\] Was found [llength ${verif_config_files}] verification test(s)"

        foreach tcl_file ${verif_config_files} {
            source ${tcl_file}
        }
    }
}