



proc make_project {rtl_path meminit_path} {

    set files_sv  [findFiles ${rtl_path} "*.sv"]
    set files_svh [findFiles ${rtl_path} "*.svh"]
    set files_v   [findFiles ${rtl_path} "*.v"]
    set files_mem [findFiles ${meminit_path} "*.mem"]

    vivado_add_files ${files_sv}  sources_1 {}
    vivado_add_files ${files_svh} sources_1 "Verilog Header"
    vivado_add_files ${files_v}   sources_1 {}
    vivado_add_files ${files_mem} sources_1 "Memory Initialization Files"

}