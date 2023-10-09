`ifndef __BUS_SEQUENCER_INTERFACE_SV
`define __BUS_SEQUENCER_INTERFACE_SV


interface bus_sequencer_interface(input logic clk, nrst);

    //**************************************************************************
    // Declaration of Signals
    //**************************************************************************
    logic start_i, ready_o;
    logic [31 : 0] start_addr_i;
    //Bus read data
    logic bus_data_valid_o;
    logic [7:0] bus_data_o;
    //SPI
    logic spi_sclk_o, spi_ncs_o, spi_mosi_o, spi_miso_i;
    // //SPI half-duplex
    //logic spi_data_o, logic spi_data_t, spi_data_i;
    //I2C SCL
    logic i2c_scl_o, i2c_scl_t, i2c_scl_i;
    //I2C SDA
    logic i2c_sda_o, i2c_sda_t, i2c_sda_i;

    //**************************************************************************
    // clocking block and modport declaration for driver 
    //**************************************************************************
    clocking dr_cb@(posedge clk) ;
        output start_i, start_addr_i, spi_miso_i, i2c_scl_i, i2c_sda_i;
        input  ready_o, bus_data_valid_o, bus_data_o, spi_sclk_o, spi_ncs_o,
            spi_mosi_o, i2c_scl_o, i2c_scl_t, i2c_sda_o, i2c_sda_t;
    endclocking

    modport DRV (clocking dr_cb, input clk, nrst);

    //**************************************************************************
    // clocking block and modport declaration for monitor
    //**************************************************************************
    clocking rc_cb@(negedge clk) ;
        input  start_i, start_addr_i, spi_miso_i, i2c_scl_i, i2c_sda_i;
        output ready_o, bus_data_valid_o, bus_data_o, spi_sclk_o, spi_ncs_o,
            spi_mosi_o, i2c_scl_o, i2c_scl_t, i2c_sda_o, i2c_sda_t;
    endclocking

    modport RCV (clocking rc_cb, input clk, nrst);

endinterface

`endif //__BUS_SEQUENCER_INTERFACE_SV