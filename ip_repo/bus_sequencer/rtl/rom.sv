

module rom #(
    parameter int ROM_DEPTH = 16,
    parameter int DATA_WIDTH = 13,
    parameter INIT_FILE_NAME = "file.mem"
)(
    input  logic clk_i,
    input  logic [31 : 0] addr_i,
    input  logic rden_i,
    output logic [DATA_WIDTH-1 : 0] data_o
);

//Local parameters
localparam int ADDR_WIDTH = $clog2(ROM_DEPTH);

//Variables
logic [DATA_WIDTH-1 : 0] data_reg;
logic [DATA_WIDTH-1 : 0] rom_arr [ROM_DEPTH];
logic [ADDR_WIDTH-1 : 0] rd_addr;

initial begin
    $readmemb(INIT_FILE_NAME, rom_arr, 0, ROM_DEPTH-1);
end

always_comb rd_addr <= addr_i[ADDR_WIDTH-1 : 0];

always_ff @(posedge clk_i) begin
    if (rden_i)
        data_reg <= rom_arr[rd_addr];
end

always_comb data_o <= data_reg;

endmodule