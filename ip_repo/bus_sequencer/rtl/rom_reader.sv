

module rom_reader #(
    parameter int ROM_DEPTH  = 8,
    parameter int JMP_WIDTH  = 8
) (
    input  logic clk_i,
    input  logic nrst_i,

    input  logic load_start_i,
    input  logic read_next_i,
    input  logic [JMP_WIDTH-1 : 0] jmp_value_i,
    input  logic jmp_dir_up_i,
    input  logic jmp_en_i,

    input  logic [31:0] start_addr_i,
    output logic [31:0] rom_addr_o,
    output logic rom_data_rdy_o
);

//Local parameters ********************************************************************************
localparam int ADDR_WIDTH = $clog2(ROM_DEPTH);


//Variables ***************************************************************************************
logic [ADDR_WIDTH-1 : 0] addr_cnt, jmp_addr_next, addr_next;
logic [1:0] rom_data_rdy_reg;


//Read address counter ****************************************************************************
always_ff @(posedge clk_i) begin
    if (load_start_i)
        addr_cnt <= start_addr_i[ADDR_WIDTH-1 : 0];
    else if (read_next_i)
        if (jmp_en_i)
            addr_cnt <= jmp_addr_next;
        else
            addr_cnt <= addr_next;
end


//Calculate next address **************************************************************************
always_comb addr_next     <= addr_cnt + 'd1;
always_comb jmp_addr_next <= (jmp_dir_up_i) ? (addr_cnt + jmp_value_i) : (addr_cnt - jmp_value_i);


//Pipe delay for ROM data ready *******************************************************************
always_ff @(posedge clk_i) begin
    rom_data_rdy_reg <= {rom_data_rdy_reg[0], (load_start_i | read_next_i)};
end


//Outputs *****************************************************************************************
always_comb rom_addr_o[ADDR_WIDTH-1 : 0] <= addr_cnt;
always_comb rom_addr_o[31 : ADDR_WIDTH] <= '0;
always_comb rom_data_rdy_o <= rom_data_rdy_reg[1];

endmodule