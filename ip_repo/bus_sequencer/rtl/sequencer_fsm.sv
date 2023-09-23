`include "bus_sequencer_pkg.svh"

module sequencer_fsm import bus_sequencer_pkg::*; #(
    
)(
    input  logic clk_i,
    input  logic nrst_i,

    input  logic start_i,
    output logic ready_o,

    //ROM
    output logic load_start_addr_o,
    output logic read_next_o,
    //From decoder
    input  cmd_t cmd_type_i,
    input  instr_t instr_type_i,
    input  instr_data_t instr_data_i,


    input  logic rom_data_rdy_i,
    input  logic bus_done_i

);

//Variables ***************************************************************************************
logic rom_read_next_reg = '0, ready_reg = '0, load_start_addr_reg = '0;
instr_data_t wait_cnt;


//FSM *********************************************************************************************
typedef enum logic [7:0] { 
    IDLE,
    ROM_READ,
    CHEK_CMD_WORD,
    WAIT_BUS,
    SEQ_STOP,
    SEQ_PAUSE,
    SEQ_CMP,
    SEQ_WAIT
} fsm_t;

fsm_t state = IDLE;

always_ff @(posedge clk_i) begin
    if (!nrst_i) begin
        state <= IDLE;
        {rom_read_next_reg, ready_reg, wait_cnt, load_start_addr_reg} <= '0;
    end else begin
        {rom_read_next_reg, load_start_addr_reg} <= '0;
        case(state)

            IDLE: begin
                ready_reg <= '1;
                if (start_i) begin
                    ready_reg <= '0;
                    load_start_addr_reg <= '1;
                    state <= ROM_READ;
                end
            end

            ROM_READ: begin
                if (rom_data_rdy_i)
                    state <= CHEK_CMD_WORD;
            end

            CHEK_CMD_WORD: begin
                if (RUN_TRANSFER == cmd_type_i) begin
                    state <= WAIT_BUS;
                end else if (INSTR_STOP == instr_type_i) begin
                    state <= SEQ_STOP;
                end else if (INSTR_PAUSE == instr_type_i) begin
                    state <= SEQ_PAUSE;
                end else if (INSTR_WAIT == instr_type_i) begin
                    wait_cnt <= instr_data_i;
                    state <= SEQ_WAIT;
                end else if (INSTR_WAIT == instr_type_i) begin
                    state <= SEQ_CMP;
                end else begin
                    rom_read_next_reg <= '1;
                    state <= ROM_READ;
                end
            end

            WAIT_BUS: begin
                if (bus_done_i) begin
                    rom_read_next_reg <= '1;
                    state <= ROM_READ;
                end
            end

            SEQ_STOP: begin
                if (!start_i) begin
                    state <= IDLE;
                end
            end

            SEQ_PAUSE: begin
                if (start_i) begin
                    rom_read_next_reg <= '1;
                    state <= ROM_READ;
                end
            end

            SEQ_WAIT: begin
                wait_cnt <= wait_cnt - 'd1;
                if ('d1 == wait_cnt) begin
                    rom_read_next_reg <= '1;
                    state <= ROM_READ;
                end
            end

            SEQ_CMP: begin
                state <= SEQ_CMP; // ?
            end

            default: begin
                state <= IDLE;
            end
        endcase
    end
end


//Outputs *****************************************************************************************
always_comb read_next_o <= rom_read_next_reg;
always_comb load_start_addr_o <= load_start_addr_reg;
always_comb ready_o     <= ready_reg;

endmodule