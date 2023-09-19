

module bus_sequencer #(
    parameter int PIN_DIR_TO_OUTPUT = 0,
    parameter int ADDRESS_WIDTH     = 8,
    parameter BUS_TYPE              = "I2C",        //Can be "I2C", "SPI"   
    parameter INIT_FILE_NAME        = ""
)(
    input  logic clk_i,
    input  logic nrst_i,

    //Control inputs
    input  logic start_i,
    input  logic [ADDRESS_WIDTH-1 : 0] start_addr_i,
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
localparam int ROM_DATA_WIDTH = protocol_sequncer_pkg::get_word_width();


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
end


//Variables ***************************************************************************************
logic rom_rden_o;
logic [ROM_DATA_WIDTH-1 : 0] rom_data_i;
logic [ADDRESS_WIDTH-1 : 0] rom_addr_o;


//ROM with sequnce ********************************************************************************
rom #(
    .ADDRESS_WIDTH(ADDRESS_WIDTH),
    .DATA_WIDTH(ROM_DATA_WIDTH),
    .INIT_FILE_NAME(INIT_FILE_NAME)
) rom_inst (
    .addr_i(rom_addr_o),
    .rden_i(rom_rden_o),
    .data_o(rom_data_i),
    .*
);


//ROM reader **************************************************************************************
bus_sequencer_reader #(
    .ROM_DATA_WIDTH(ROM_DATA_WIDTH),
    .BUS_TYPE(BUS_TYPE)
) bus_sequencer_reader_inst (
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