

package protocol_sequncer_pkg

    typedef enum logic { 
        RUN_TRANSFER = 1'b1,
        RUN_INSTR    = 1'b0
    } cmd_t;

    typedef enum logic [2:0] {
        INSTR_WAIT          = 3'h0,
        INSTR_COMPARE       = 3'h1,
        INSTR_COMP_JMP      = 3'h2,
        INSTR_END           = 3'h3,
        INSTR_PAUSE         = 3'h4,
        INSTR_UNCOND_JMP    = 3'h5,
        INSTR_UNUSED1       = 3'h6,
        INSTR_UNUSED2       = 3'h7,
    } instr_t;

    typedef enum logic { 
        COMPARE_LAST = 1'b1,
        COMPARE_NOT_LAST = 1'b0
    } instr_compare_conf_t;

    typedef enum logic { 
        JUMP_UP = 1'b1,
        JUMP_DOWN = 1'b0
    } instr_jmp_config_t;

    typedef logic [7:0] instr_data_t;
    

    //I2C type defines ****************************************************************************
    typedef struct packed {
        logic ack;
        logic write;
        logic stop;
        logic start;
    } i2c_transfer_config_t;

    // typedef struct packed {
    //     instr_data_t data;
    //     i2c_transfer_config_t cnfg;
    //     cmd_t cmd_type;
    // } i2c_transfer_t;


    //SPI type defines ****************************************************************************
    typedef struct packed {
        logic [2:0] unused;
        logic write;
    } spi_transfer_config_t;

    // typedef struct packed {
    //     instr_data_t data;
    //     spi_transfer_config_t cnfg;
    //     cmd_t cmd_type;
    // } spi_transfer_t;


    //Bus transfer types **************************************************************************
    type union packed {
        spi_transfer_config_t spi;
        i2c_transfer_config_t i2c;
    } transfer_config_ut;


    typedef struct packed {
        instr_data_t data;
        transfer_config_ut cnfg;
        cmd_t cmd_type;
    } protocol_transfer_t;

endpackage