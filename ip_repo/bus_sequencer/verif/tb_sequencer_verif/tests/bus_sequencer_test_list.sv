`ifndef __BUS_SEQUENCER_TEST_LIST_SV
`define __BUS_SEQUENCER_TEST_LIST_SV

package bus_sequencer_test_list;

    import uvm_pkg::*;
    `include "uvm_macros.svh"

    import bus_sequencer_env_pkg::*;
    import bus_sequencer_seq_list::*;


    //**************************************************************************
    // including test list
    //**************************************************************************

    `include "bus_sequencer_basic_test.sv"

endpackage

`endif //__BUS_SEQUENCER_TEST_LIST_SV