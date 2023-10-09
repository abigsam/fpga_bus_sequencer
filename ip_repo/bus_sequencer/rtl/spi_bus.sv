
module spi_bus #(
    parameter int CPOL              = 0,
    parameter int CPHA              = 0,
    parameter bit PIN_DIR_TO_OUTPUT = 1'b0,
    parameter int INPUT_CLOCK_HZ    = 100000000,
    parameter int SCLK_HZ           = 1000000
)(
    input  logic clk_i,
    input  logic nrst_i,

    //Control signals


    //SPI
    output logic spi_sclk_o,
    output logic spi_ncs_o,
    output logic spi_mosi_o,
    input  logic spi_miso_i
);

//Local parameters
localparam int SCLK_DIV = INPUT_CLOCK_HZ / SCLK_HZ / 2;
localparam int DIC_CNT_WIDTH = $clog2(SCLK_DIV);





endmodule