`ifndef __BUS_SEQUENCER_PKG
`define __BUS_SEQUENCER_PKG

package bus_sequencer_pkg;

    //Common types ********************************************************************************
    typedef enum logic { 
        RUN_TRANSFER = 1'b1,
        RUN_INSTR    = 1'b0
    } cmd_t;

    typedef enum logic [2:0] {
        INSTR_WAIT          = 3'h0,
        INSTR_COMPARE       = 3'h1,
        INSTR_COMP_JMP      = 3'h2,
        INSTR_STOP          = 3'h3,
        INSTR_PAUSE         = 3'h4,
        INSTR_UNCOND_JMP    = 3'h5,
        INSTR_UNUSED1       = 3'h6,
        INSTR_UNUSED2       = 3'h7
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


    //SPI type defines ****************************************************************************
    typedef struct packed {
        logic [2:0] unused;
        logic write;
    } spi_transfer_config_t;


    //Bus transfer types **************************************************************************
    typedef union packed {
        spi_transfer_config_t spi;
        i2c_transfer_config_t i2c;
    } transfer_config_ut;

    typedef union packed {
        logic unused;
        instr_compare_conf_t compare_type;
        instr_jmp_config_t   jmp_dir;
    } instr_config_ut;

    typedef struct packed {
        instr_data_t data;
        transfer_config_ut cnfg;
    } bus_transfer_word_t;

    typedef struct packed {
        instr_data_t data;
        instr_config_ut cnfg;
        instr_t instruction;
    } instr_word_t;

    typedef union packed {
        instr_word_t instr_word;
        bus_transfer_word_t bus_word;
    } word_ut;

    typedef struct packed {
        word_ut code;
        cmd_t cmd_type;
    } seq_word_t;



    //Functions ***********************************************************************************
    function int get_word_width();
        return $bits(seq_word_t);
    endfunction

    function int get_jmp_width();
        return $bits(instr_data_t);
    endfunction
    
    function cmd_t get_word_type(input seq_word_t in_word);
        return in_word.cmd_type;
    endfunction

    function instr_t get_instruction_type(input seq_word_t in_word);
        return in_word.code.instr_word.instruction;
    endfunction

    function instr_data_t get_instruction_data(input seq_word_t in_word);
        return in_word.code.instr_word.data;
    endfunction

    function logic is_bus_transfer(input seq_word_t in_word);
        return (in_word.cmd_t == RUN_TRANSFER);
    endfunction

endpackage

`endif //__BUS_SEQUENCER_PKG