`include "bus_sequencer_pkg.svh"

`define ROM_START_ADDR      (32'h0)
`define CLOCK_PERIOD        (10ns)


module tb_basic ();

localparam int PIN_DIR_TO_OUTPUT = 0;
localparam int ROM_WORDS_DEPTH   = 16;
localparam BUS_TYPE              = "I2C";
localparam INIT_FILE_NAME        = "test.mem";
//


//IOs *********************************************************************************************
logic clk_i, nrst_i, start_i, ready_o, bus_data_valid_o;
logic [31 : 0] start_addr_i;
logic [7:0] bus_data_o;
logic spi_sclk_o, spi_ncs_o, spi_mosi_o, spi_miso_i;
// logic spi_data_o, spi_data_t, spi_data_i;
logic i2c_scl_o, i2c_scl_t, i2c_scl_i;
logic i2c_sda_o, i2c_sda_t, i2c_sda_i;


//DUT *********************************************************************************************
bus_sequencer_top #(
    .PIN_DIR_TO_OUTPUT(PIN_DIR_TO_OUTPUT),
    .ROM_WORDS_DEPTH(ROM_WORDS_DEPTH),
    .BUS_TYPE(BUS_TYPE),
    .INIT_FILE_NAME(INIT_FILE_NAME)
) DUT (
    .*
);


//Generate clock **********************************************************************************
always #(`CLOCK_PERIOD/2) clk_i = ~clk_i;


//Basic tests *************************************************************************************
initial begin
    nrst_i = '1;
    {clk_i, start_i, start_addr_i, spi_miso_i, i2c_scl_i, i2c_sda_i} = '0;

    

    #1us;
    $finish();
end

endmodule