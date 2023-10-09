

module i2c_bus #(
    parameter bit PIN_DIR_TO_OUTPUT = 1'b0,
    parameter int INPUT_CLOCK_HZ = 100000000,
    parameter int SCL_CLOCK_HZ   = 100000
)(
    input  logic clk_i,
    input  logic nrst_i,

    //Control IOs
    input  logic bus_enable,
    input  logic cmd_valid,
    input  i2c_transfer_config_t bus_config_i,
    output logic bus_ready_o,
    input  instr_data_t data_i,
    output instr_data_t data_o,
    output logic data_out_valid,

    //I2C SCL
    output logic i2c_scl_o,
    output logic i2c_scl_t,
    input  logic i2c_scl_i,
    //I2C SDA
    output logic i2c_sda_o,
    output logic i2c_sda_t,
    input  logic i2c_sda_i
);

//Local parameters
localparam bit I2C_MST_DIR_OUT = 1'b0;
localparam int I2C_MST_DIV = INPUT_CLOCK_HZ / (SCL_CLOCK_HZ * 4); //Divider by 4 -- is from I2C core
localparam logic [6:0] I2C_MST_ADDR = 7'b111_1110;

//Variables
logic [6:0] my_addr; // Slave address input
logic rst;     // synchronous active high reset
logic ena;     // core enable signal
logic sl_cont;
// control inputs
logic start;
logic stop;
logic read;
logic write;
logic ack_in;
logic [7:0] din;
// status outputs
logic cmd_ack;
logic ack_out;
logic i2c_busy;
logic i2c_al;
logic [7:0] dout;
// I2C signals
logic slave_en;


i2c_master_byte_ctrl i2c_master_byte_ctrl_inst (
    .clk(clk_i),
    .nReset(nrst_i),
    .scl_i(i2c_scl_i),
    .scl_o(i2c_scl_o),
    .scl_oen(scl_oen),
    .sda_i(i2c_sda_i),
    .sda_o(i2c_sda_o),
    .sda_oen(sda_oen),
    .clk_cnt(I2C_MST_DIV),
    .*
);


//Unused
always_comb sl_cont <= '0;
always_comb ena <= bus_enable;
always_comb my_addr <= I2C_MST_ADDR;


//Connect direction pins
always_comb i2c_scl_t <= (PIN_DIR_TO_OUTPUT == I2C_MST_DIR_OUT) ? scl_oen : ~scl_oen;
always_comb i2c_sda_t <= (PIN_DIR_TO_OUTPUT == I2C_MST_DIR_OUT) ? sda_oen : ~sda_oen;


//Control I2c master signals
always_comb read  <= cmd_valid & bus_config_i.read;
always_comb write <= cmd_valid & bus_config_i.write;
always_comb stop  <= cmd_valid & bus_config_i.stop;
always_comb start <= bus_config_i.stop;
always_comb ack_in <= bus_config_i.ack;
always_comb din      <= data_i;
always_comb data_o <= dout;

//
// always_comb cmd_done <= ;
always_comb bus_ready_o <= ~(i2c_busy | i2c_al);


endmodule