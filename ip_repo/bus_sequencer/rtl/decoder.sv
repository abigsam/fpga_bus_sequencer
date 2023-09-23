`include "bus_sequencer_pkg.svh"

module decoder import bus_sequencer_pkg::*; #(

)(
    input  logic [get_word_width()-1 : 0] word_i,


    //
    output cmd_t cmd_type,
    output instr_t instr_type,
    output instr_data_t instr_data,



    //JMP command
    output logic [get_jmp_width()-1 : 0] jmp_value,
    output logic jmp_dir_up,
    output logic jmp_en


);

//Variables
seq_word_t in_word;
instr_t current_instr;
logic is_instruction;

//Internal
always_comb in_word  <= {word_i};
always_comb current_instr <= get_instruction_type(in_word);
always_comb is_instruction <= in_word.cmd_type == RUN_INSTR;


always_comb cmd_type   <= get_word_type(in_word);
always_comb instr_type <= get_instruction_type(in_word);
always_comb instr_data <= get_instruction_data(in_word);


//Outputs *****************************************************************************************
always_comb jmp_value  <= in_word.code.instr_word.data;
always_comb jmp_dir_up <= in_word.code.instr_word.cnfg.jmp_dir == JUMP_UP;
always_comb jmp_en     <= is_instruction && ((INSTR_COMP_JMP == current_instr) || (INSTR_UNCOND_JMP == current_instr));


endmodule