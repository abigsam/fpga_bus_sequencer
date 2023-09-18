

module bus_sequencer_reader #(
    parameter int ROM_DATA_WIDTH = 13,
    parameter int ROM_ADDR_WIDTH = 8,
    parameter BUS_TYPE = "I2C"
)(
    input  logic clk_i,
    input  logic nrst_i

    input  logic start_i,
    input  logic [ADDRESS_WIDTH-1 : 0] start_addr_i,
    output logic ready_o,

    output logic rom_rden_o,
    output logic [ROM_ADDR_WIDTH-1 : 0] rom_addr_o,
    input  logic [ROM_DATA_WIDTH-1 : 0] rom_data_i
);


//Variables
word_ut rom_word;


always_comb rom_word <= rom_data_i;


endmodule