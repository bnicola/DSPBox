
module nco #(
   //------------------------------------------------------
   //--				External Parameters	                       --
   //------------------------------------------------------
   parameter integer WAVE_WIDTH       = 16,         // Our wave signal bit width
   parameter integer LOOKUP_TBL_SIZE  = 128,       // Our waveform lookup table size
   parameter integer SCALE_INT_WIDTH  = 2,          // 1 bit integer as we only have a gain 0.0 --> 1.0
   parameter integer SCALE_Q_WIDTH    = 14,         // 15 bit fraction
   parameter integer OUTPUT_WIDTH     = WAVE_WIDTH  // Output width
)
(
  //------------------------------------------------------
  //--				Input/output Ports Parameters	            --
  //------------------------------------------------------
  input                                                     clk,            // clock input
  input                                                     rst,            // reset input
  input             [31:0]                                  freq_in,        // frequency input
  input             [SCALE_INT_WIDTH + SCALE_Q_WIDTH - 1:0] scale_factor,   // a scale factor(0.0-1.0)
  input             [12:0]                                  phase,          // intial phase
  output reg signed [WAVE_WIDTH - 1:0]                      sine_out,       // sine output
  output reg signed [WAVE_WIDTH - 1:0]                      cos_out,        // cos output
  output reg signed [WAVE_WIDTH - 1:0]                      scaled_sine_out // scaled sine output
);

parameter lookup_bits = $clog2(LOOKUP_TBL_SIZE);
parameter AMPLITUDE = 2**(WAVE_WIDTH - 1) - 1;

reg [31:0] phase_accumulator; // phase accumulator

reg [31:0] sine_lut [0:LOOKUP_TBL_SIZE - 1]; // sine lookup table
reg [31:0] cos_lut  [0:LOOKUP_TBL_SIZE - 1]; // cosine lookup table 

reg [31:0] phase_increment;
reg signed [WAVE_WIDTH + SCALE_INT_WIDTH + SCALE_Q_WIDTH:0] scaled_wave;
reg [lookup_bits:0] initial_phase;

wire [lookup_bits - 1:0] current_phase;

// Generate sine lookup table
integer i;
initial begin
  for (i = 0; i < LOOKUP_TBL_SIZE; i = i + 1) begin
    sine_lut[i] = ($sin((2.0 * 3.1418 * i) / LOOKUP_TBL_SIZE) * AMPLITUDE);
    cos_lut[i]  = ($cos((2.0 * 3.1418 * i) / LOOKUP_TBL_SIZE) * AMPLITUDE);
  end
end

// 360 ---> table size
// x   --->    ?
// Then to get 90 degrees--> initial_phase = (90/360 * table_size)
always @ (posedge clk or posedge rst) begin
   if (rst) begin
      initial_phase <= 0;
   end
   else begin
      initial_phase <= phase;
   end
end

always @ (posedge clk or posedge rst) begin
   if (rst) begin
      phase_increment <= 0;
   end
   else begin
      phase_increment <= freq_in; // 2^31 * f/clk *LOOKUP_TBL_SIZE, 2kHz -->85899, 50k-->2147484
   end
end

always @ (posedge clk or posedge rst) begin
  if (rst) begin
    phase_accumulator <= 0;
  end else begin
    phase_accumulator <= phase_accumulator + phase_increment;
  end
end

assign current_phase = phase_accumulator[31:32-lookup_bits] + initial_phase;

always @ (posedge clk) begin
  sine_out <= sine_lut[current_phase];
  cos_out <= cos_lut[current_phase];
end

always @ (posedge clk) begin
  scaled_wave <= $signed(sine_out) * $signed(scale_factor) >>> (SCALE_Q_WIDTH);
  scaled_sine_out = $signed(scaled_wave[OUTPUT_WIDTH - 1: 0]);
  cos_out <= cos_lut[current_phase];
end

endmodule
