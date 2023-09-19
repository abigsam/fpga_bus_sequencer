

module rom #(
    parameter int ADDR_WIDTH = 8,
    parameter int DATA_WIDTH = 13,
    parameter INIT_FILE_NAME = "file.mem"
)(
    input  logic clk_i,
    input  logic [ADDR_WIDTH-1 : 0] addr_i,
    input  logic rden_i,
    output logic [DATA_WIDTH-1 : 0] data_o
);

localparam int ROM_DEPTH = 2**ADDR_WIDTH;

logic [DATA_WIDTH-1 : 0] data_reg;

logic [DATA_WIDTH-1 : 0] rom_arr [ROM_DEPTH];

initial begin
    $readmemb(INIT_FILE_NAME, rom_arr);
end

always_ff @(posedge clk_i) begin
    if (rden_i)
        data_reg <= rom_arr[addr_i];
end

always_comb data_o <= data_reg;

endmodule