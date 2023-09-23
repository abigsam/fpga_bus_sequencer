`include "bus_sequencer_pkg.svh"

module bus_sequencer_top #(
    parameter int PIN_DIR_TO_OUTPUT = 0,
    parameter int ROM_WORDS_DEPTH   = 16,
    parameter BUS_TYPE              = "I2C",        //Can be "I2C", "SPI"   
    parameter INIT_FILE_NAME        = "test.mem"
)(
    input  logic clk_i,
    input  logic nrst_i,

    //Control inputs
    input  logic start_i,
    input  logic [31 : 0] start_addr_i,
    output logic ready_o,

    //Bus read data
    output logic bus_data_valid_o,
    output logic [7:0] bus_data_o,
    
    //SPI
    output logic spi_sclk_o,
    output logic spi_ncs_o,
    output logic spi_mosi_o,
    input  logic spi_miso_i,
    // //SPI half-duplex
    // output logic spi_data_o,
    // output logic spi_data_t,
    // input  logic spi_data_i,

    //I2C SCL
    output logic i2c_scl_o,
    output logic i2c_scl_t,
    input  logic i2c_scl_i,
    //I2C SDA
    output logic i2c_sda_o,
    output logic i2c_sda_t,
    input  logic i2c_sda_i
);

//Local parameters ********************************************************************************
localparam int ROM_DATA_WIDTH = bus_sequencer_pkg::get_word_width();
localparam int ROM_ADDR_WIDTH = $clog2(ROM_WORDS_DEPTH);
localparam int DEFAULT_ADDR_WIDTH = 32;
localparam int JMP_VALUE_WIDTH = bus_sequencer_pkg::get_jmp_width();


//Check parameters ********************************************************************************
initial begin
    if (INIT_FILE_NAME == "") begin
        $error("bus_sequencer_error: memory init file parameter INIT_FILE_NAME cannot be empty");
        $finish();
    end else begin
        $display("bus_sequencer_info: internal ROM will be inited with file %0s", INIT_FILE_NAME);
    end
    if (BUS_TYPE != "SPI" && BUS_TYPE != "I2C") begin
        $error("bus_sequencer_error: parameter BUS_TYPE can be SPI, I2C. But received %0s", BUS_TYPE);
        $finish();
    end
    if ($clog2(ROM_WORDS_DEPTH) > DEFAULT_ADDR_WIDTH) begin
        $error("bus_sequencer_error: unsupported number of ROM words --> %0d", ROM_WORDS_DEPTH);
        $finish();
    end
end


//Variables ***************************************************************************************
logic rom_rden;
logic [ROM_DATA_WIDTH-1 : 0] rom_data;
logic [DEFAULT_ADDR_WIDTH-1 : 0] rom_addr;
logic load_start_addr;
//From decoder
logic [JMP_VALUE_WIDTH-1 : 0] jmp_value;
logic jmp_dir_up, jmp_en;
bus_sequencer_pkg::cmd_t cmd_type;
bus_sequencer_pkg::instr_t instr_type;
bus_sequencer_pkg::instr_data_t instr_data;


//ROM with sequnce ********************************************************************************
rom #(
    .ROM_DEPTH(ROM_WORDS_DEPTH),
    .DATA_WIDTH(ROM_DATA_WIDTH),
    .INIT_FILE_NAME(INIT_FILE_NAME)
) rom_inst (
    .addr_i(rom_addr),
    .rden_i(rom_rden),
    .data_o(rom_data),
    .*
);

//ROM reader **************************************************************************************
rom_reader #(
    .ROM_DEPTH(ROM_WORDS_DEPTH),
    .JMP_WIDTH(JMP_VALUE_WIDTH)
) rom_reader_inst (
    .load_start_i(load_start_addr),
    .jmp_value_i(jmp_value),
    .jmp_dir_up_i(jmp_dir_up),
    .jmp_en_i(jmp_en),
    .read_next_i(read_next),
    .rom_addr_o(rom_addr),
    .rom_data_rdy_o(rom_data_rdy),
    .*
);


//Word decoder ***********************************************************************************
decoder #()
decoder_inst (
    .word_i(rom_data),
    .*
);


//Main FSM ****************************************************************************************
sequencer_fsm sequencer_fsm_inst (
    .load_start_addr_o(load_start_addr),
    .read_next_o(read_next),
    .cmd_type_i(cmd_type),
    .instr_type_i(instr_type),
    .instr_data_i(instr_data),
    .rom_data_rdy_i(rom_data_rdy),
    .bus_done_i(),
    .*
);


//Choose bus driver********************************************************************************
generate
    if (BUS_TYPE == "SPI") begin

    end
    if (BUS_TYPE == "I2C") begin

    end
endgenerate


endmodule