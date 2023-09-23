
proc mp_add_files {files fileset_name file_type} {
    if {${files} != {}} {
        add_files -norecurse -fileset ${fileset_name} ${files}
        update_compile_order -fileset ${fileset_name}
        if {${file_type} != {}} {
            set_property FILE_TYPE ${file_type} [get_files ${files}]
            update_compile_order -fileset ${fileset_name}
        }
    }
}


proc make_project {seq_ip_rtl_path} {

    set files_sv [findFiles ${seq_ip_rtl_path} "*.sv"]
    set files_svh [findFiles ${seq_ip_rtl_path} "*.svh"]
    set files_v [findFiles ${seq_ip_rtl_path} "*.v"]
    set files_mem [findFiles ${seq_ip_rtl_path} "*.mem"]

    mp_add_files ${files_sv}  sources_1 {}
    mp_add_files ${files_svh} sources_1 "Verilog Header"
    mp_add_files ${files_v}   sources_1 {}
    mp_add_files ${files_mem}   sources_1 "Memory Initialization Files"


}