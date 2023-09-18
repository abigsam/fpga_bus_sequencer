

module bus_sequencer #(
    parameter int PIN_DIR_TO_OUTPUT = 0,
    parameter int ADDRESS_WIDTH = 8,
    parameter INIT_FILE_NAME = "file.mem"
)(
    input  logic clk_i,
    input  logic nrst_i,

    input  logic start_i,
    input  logic [ADDRESS_WIDTH-1 : 0] start_addr_i,
    output logic ready_o,
    
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


//ROM with sequnce ********************************************************************************
rom #(
    .ADDRESS_WIDTH(ADDRESS_WIDTH),
    .DATA_WIDTH(13),
    .INIT_FILE_NAME(INIT_FILE_NAME)
) rom_inst (
    .addr_i(),
    .rden_i(),
    .data_o(),
    .*
);


endmodule