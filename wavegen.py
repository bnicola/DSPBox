import traceback
import math
import matplotlib.pyplot as plt
import numpy as np
from  project_dsp import  *

class wavegen:

    def __init__(self, instance_name, fs, freq, out_width, init_phase = 0, wave_table_size=1024):
        
        if instance_name is None:
            self.raise_error(self, "Missing instance_name in module")
        if fs is None:
            self.raise_error(self, "Missing fs in module")
        if freq is None:
            self.raise_error(self, "Missing freq in module")
        if out_width is None:
            self.raise_error(self, "Missing out_width in module")
       
        self.instance_name   = instance_name
        self.fs              = fs
        self.freq            = freq 
        self.init_phase      = init_phase    
        self.out_width       = out_width 
        self.wave_table_size = wave_table_size

        d = debug()
        if (d == True):
            self.unit_test()
        self.generate()
        add_file_to_list("wavegen_" + self.instance_name + ".v")

    def generate(self):
        print("...generating Wavegen with name " + self.instance_name + "...")
        freq_requested = (2**32) * self.freq/self.fs
        initial_phase = (self.init_phase/360) * self.wave_table_size
        with open(proj_name() + "wavegen_" + self.instance_name + ".v", 'w') as f:
            f.write("module wavegen_" + self.instance_name + " #(\n")
            f.write("//------------------------------------------------------\n")
            f.write("//--				External Parameters	                       --\n")
            f.write("//------------------------------------------------------\n")
            f.write("parameter integer WAVE_WIDTH       = 16,         // Our wave signal bit width\n")
            f.write("parameter integer LOOKUP_TBL_SIZE  = "+ str(self.wave_table_size) + ",       // Our waveform lookup table size\n")
            f.write("parameter integer SCALE_INT_WIDTH  = 2,          // 1 bit integer as we only have a gain 0.0 --> 1.0\n")
            f.write("parameter integer SCALE_Q_WIDTH    = 14,         // 15 bit fraction\n")
            f.write("parameter integer OUTPUT_WIDTH     = WAVE_WIDTH  // Output width\n")
            f.write(")\n")
            f.write("(\n")
            f.write("    //------------------------------------------------------\n")
            f.write("    //--				Input/output Ports Parameters	            --\n")
            f.write("    //------------------------------------------------------\n")
            f.write("    input                                                     clk,             // clock input\n")
            f.write("    input                                                     rst,             // reset input\n")
            f.write("    input             [SCALE_INT_WIDTH + SCALE_Q_WIDTH - 1:0] scale_factor,    // a scale factor(0.0-1.0)\n")
            f.write("    output reg signed [WAVE_WIDTH - 1:0]                      scaled_sine_out, // scaled sine output\n")
            f.write("    output reg signed [WAVE_WIDTH - 1:0]                      scaled_cos_out   // scaled cosine output\n")
            f.write(");\n")
            f.write("    parameter lookup_bits = $clog2(LOOKUP_TBL_SIZE);\n")
            f.write("    parameter AMPLITUDE = 2**(WAVE_WIDTH - 1) - 1;\n")
            f.write("\n")
            f.write("    reg [31:0] phase_accumulator; // phase accumulator\n")
            f.write("\n")
            f.write("    reg [31:0] sine_lut [0:LOOKUP_TBL_SIZE - 1]; // sine lookup table\n")
            f.write("    reg [31:0] cos_lut  [0:LOOKUP_TBL_SIZE - 1]; // cosine lookup table \n")
            f.write("\n")
            f.write("    reg [31:0] phase_increment;\n")
            f.write("    reg signed [WAVE_WIDTH + SCALE_INT_WIDTH + SCALE_Q_WIDTH:0] scaled_wave;\n")
            f.write("    reg signed [WAVE_WIDTH + SCALE_INT_WIDTH + SCALE_Q_WIDTH:0] scaled_wave_90;\n")
            f.write("    reg [lookup_bits:0] initial_phase;\n")
            f.write("    reg [WAVE_WIDTH - 1 : 0] sine_out;\n")
            f.write("    reg [WAVE_WIDTH - 1 : 0] cos_out;\n")
            f.write("\n")
            f.write("    wire [lookup_bits - 1:0] current_phase;\n")
            f.write("\n")
            f.write("    // Our Scaled output\n")
            f.write("    assign scaled_wave = $signed(sine_out) * $signed(scale_factor) >>> (SCALE_Q_WIDTH);\n")
            f.write("    assign scaled_sine_out = $signed(scaled_wave[OUTPUT_WIDTH - 1: 0]);\n")
            f.write("\n")
            f.write("    assign scaled_wave_90 = $signed(cos_out) * $signed(scale_factor) >>> (SCALE_Q_WIDTH);\n")
            f.write("    assign scaled_cos_out =  $signed(scaled_wave_90[OUTPUT_WIDTH - 1: 0]);\n")
            f.write("    // Generate sine lookup table\n")
            f.write("    integer i;\n")
            f.write("    initial begin\n")
            f.write("        for (i = 0; i < LOOKUP_TBL_SIZE; i = i + 1) begin\n")
            f.write("            sine_lut[i] = ($sin((2.0 * 3.1418 * i) / LOOKUP_TBL_SIZE) * AMPLITUDE);\n")
            f.write("            cos_lut[i]  = ($cos((2.0 * 3.1418 * i) / LOOKUP_TBL_SIZE) * AMPLITUDE);\n")
            f.write("        end\n")
            f.write("    end\n")
            f.write("    \n")
            f.write("    // 360 ---> table size\n")
            f.write("    // x   --->    ?\n")
            f.write("    // Then to get 90 degrees--> initial_phase = (90/360 * table_size)\n")
            f.write("    always @ (posedge clk or posedge rst) begin\n")
            f.write("        if (rst) begin\n")
            f.write("            initial_phase <= 0;\n")
            f.write("        end\n")
            f.write("        else begin\n")
            f.write("            initial_phase <= " + str(int(initial_phase)) +";\n")
            f.write("        end\n")
            f.write("    end\n")
            f.write("\n")
            f.write("    always @ (posedge clk or posedge rst) begin\n")
            f.write("        if (rst) begin\n")
            f.write("            phase_increment <= 0;\n")
            f.write("        end\n")
            f.write("        else begin\n")
            f.write("            phase_increment <= " + str(int(math.ceil(freq_requested))) + "; // 2^31 * f/clk 2kHz -->85899, 50k-->2147484, ...etc\n")
            f.write("        end\n")
            f.write("    end\n")
            f.write("\n")
            f.write("    always @ (posedge clk or posedge rst) begin\n")
            f.write("        if (rst) begin\n")
            f.write("            phase_accumulator <= 0;\n")
            f.write("        end else begin\n")
            f.write("            phase_accumulator <= phase_accumulator + phase_increment;\n")
            f.write("        end\n")
            f.write("    end\n")
            f.write("\n")
            f.write("    assign current_phase = phase_accumulator[31:32-lookup_bits] + initial_phase;\n\n")
            f.write("\n")
            f.write("    always @ (posedge clk) begin\n")
            f.write("        sine_out <= sine_lut[current_phase];\n")
            f.write("        cos_out  <= cos_lut[current_phase];\n")
            f.write("    end\n\n")
            f.write("endmodule\n")


            print("Done generating WAVEGEN " + "wavegen_" + self.instance_name + ".v\n")

    
    def unit_test(self):
        MHz = 1000000
        clk = self.fs
        clk_period = int((1/clk) * 1e9) 
        haf_clk_period = int(clk_period / 2)
        with open(proj_name() + "wavegen_" + self.instance_name + ".do", 'w') as f:
            f.write("project compileall\n")
            f.write("vsim -gui work.wavegen_" + self.instance_name + " -t ns\n")
            f.write("restart -f\n")
            f.write("view structure\n")
            f.write("view wave\n\n")
            
            f.write("add wave -noupdate -divider {nco}\n")
            f.write("add wave -noupdate -expand  -group nco\n")
            f.write("add wave -noupdate -group nco -radix hex {clk}\n")
            f.write("add wave -noupdate -group nco -radix hex {rst}\n")
            f.write("add wave -noupdate -group nco -radix dec {scaled_wave}\n")
            f.write("add wave -noupdate -group nco -color \"yellow\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {scaled_sine_out}\n")
            f.write("add wave -noupdate -group nco -color \"magenta\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {scaled_wave_90}\n")
            f.write("add wave -noupdate -group nco -radix dec {current_phase}\n")
            f.write("add wave -noupdate -group nco -radix dec {scale_factor}\n")
            f.write("add wave -noupdate -group nco -radix dec {initial_phase}\n")
            f.write("add wave -noupdate -group nco -radix dec {phase_increment}\n")
            f.write("add wave -noupdate -group nco -radix dec {phase_accumulator}\n")
            f.write("add wave -noupdate -group nco -radix dec {sine_lut}\n\n")
            
            f.write("force -freeze clk 1 0, 0 {" + str(haf_clk_period) +  " ns} -r " + str(clk_period) + "\n")

            f.write("force -freeze sim:/rst 1 0\n")
            f.write("force -freeze sim:/rst 0 100\n")
            f.write("#20kHz 2^32*f/fs(where fs = clk = 100MHz)\n")
            f.write("#so for x Hz ==> 2^32 * x / 100MHz\n")
         
            f.write("#14 bits fraction * 1.0\n")
            f.write("force -freeze sim:/scale_factor 10#16384 0\n") 
            f.write("#14 bits fraction * 0.5\n")
            f.write("force -freeze sim:/scale_factor 10#8196 40000 \n")
            f.write("#14 bits fraction * 0.25\n")
            f.write("force -freeze sim:/scale_factor 10#4096 120000 \n\n")

            f.write("WaveRestoreZoom {0 ns} {1000 ns}\n")
            f.write("TreeUpdate [SetDefaultTree]\n")
            f.write("WaveRestoreCursors {130 ns}\n")
            f.write("configure wave -namecolwidth 212\n")
            f.write("configure wave -valuecolwidth 120\n")
            f.write("configure wave -justifyvalue left\n")
            f.write("configure wave -signalnamewidth 0\n")
            f.write("configure wave -snapdistance 10\n")
            f.write("configure wave -datasetprefix 0\n")
            f.write("configure wave -rowmargin 4\n")
            f.write("configure wave -childrowmargin 2 \n\n")
            
            f.write("run 200000\n")
            f.write("wave zoom full\n")

    def raise_error(self, error):
        line_no = traceback.extract_stack()[0].lineno
        raise ValueError(error + " at " + str(line_no))
    



        