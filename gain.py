import traceback
import math
import matplotlib.pyplot as plt
import numpy as np
from  project_dsp import  *

class gain:

    def __init__(self, instance_name, fs, gain = 1, signal_width=16, gain_int_width=4, gain_q_width=12, out_width=16):
        
        if instance_name is None:
            self.raise_error(self, "Missing instance_name in module")
       
        self.instance_name   = instance_name
        self.fs              = fs
        self.gain            = gain
        self.signal_width    = signal_width
        self.gain_int_width  = gain_int_width 
        self.gain_q_width    = gain_q_width    
        self.out_width       = out_width 
        
        self.out_width = self.get_required_bits(gain * (2**signal_width))
        d = debug()
        if (d == True):
            self.unit_test()
        self.generate()
        add_file_to_list("gain_" + self.instance_name + ".v")

    def generate(self):
        print("...generating Gain with name " + self.instance_name + "...")
        scale = 2**(self.gain_q_width - 1)
        gain = int(math.ceil(self.gain * scale))
        with open(proj_name() + "gain_" + self.instance_name + ".v", 'w') as f:
            f.write("module gain#\n")
            f.write("(\n")
            f.write("    parameter integer IN_SIG_WIDTH    = " + str(self.signal_width) + ",\n")
            f.write("    parameter integer GAIN_INT_WIDTH  = " + str(self.gain_int_width) + ",\n")
            f.write("    parameter integer GAIN_Q_WIDTH    = " + str(self.gain_q_width) + ",\n")
            f.write("    parameter integer RESULT_WIDTH    = " + str(self.out_width) + "\n")
            f.write(")\n")
            f.write("(\n")
            f.write("    input clk, rst,\n")
            f.write("    input signed [IN_SIG_WIDTH - 1:0] signal_in,\n")
            #f.write("    input [GAIN_INT_WIDTH + GAIN_Q_WIDTH - 1:0] gain_in,\n")
            f.write("    output reg signed [RESULT_WIDTH - 1:0] result\n")
            f.write(");\n\n")
            f.write("    wire signed [GAIN_INT_WIDTH + GAIN_Q_WIDTH - 1:0] gain_in;\n")
            f.write("    reg signed [IN_SIG_WIDTH + GAIN_INT_WIDTH + GAIN_Q_WIDTH - 1 :0] product;\n")
            if (debug()):
                f.write("    wire signed [IN_SIG_WIDTH - 1:0] f1_sine;\n")
                f.write("    wire signed [IN_SIG_WIDTH - 1:0] f1_cos;\n")
                f.write("    wire signed [IN_SIG_WIDTH - 1:0] f1_scaled_sine_out;\n")
                f.write("    wire [31:0] f1;\n\n")

                f.write("    nco #(IN_SIG_WIDTH) input_signal_1  (\n")
                f.write("        .clk(clk), \n")
                f.write("        .rst(rst),\n") 
                f.write("        .freq_in(f1),\n")
                f.write("        .scale_factor(8190),\n") 
                f.write("        .phase(0), \n")
                f.write("        .sine_out(f1_sine),\n") 
                f.write("        .cos_out(f1_cos),\n")
                f.write("        .scaled_sine_out(f1_scaled_sine_out)\n")
                f.write("    );\n")
            f.write("\n")
            f.write("    always @(posedge clk , posedge rst) begin\n")
            f.write("        if (rst) begin \n")
            f.write("            product <= 0;\n")
            f.write("        end\n")
            f.write("        else begin \n")
            f.write("            // Perform fixed-point multiplication with scaling\n")
            if (debug()):
                f.write("            product = ($signed(f1_scaled_sine_out) * $signed(gain_in)); \n")
            else:
                f.write("            product = ($signed(signal_in) * $signed(gain_in));\n")
            f.write("        end\n")
            f.write("    end\n")
            f.write("\n")
            f.write("    assign gain_in = $signed(" + str(gain) + ");\n")
            f.write("    assign result = (product >>> GAIN_Q_WIDTH - 1);\n")
            f.write("\n")
            f.write("endmodule\n")

            print("Done generating GAIN " + "gain_" + self.instance_name + ".v\n")

    
    def unit_test(self):
        MHz = 1000000
        clk = self.fs
        clk_period = int((1/clk) * 1e9) 
        haf_clk_period = int(clk_period / 2)
        with open(proj_name() + "gain_" + self.instance_name + ".do", 'w') as f:
            f.write("project compileall\n")
            f.write("vsim -gui work.gain -t ns\n")
            f.write("restart -f\n")
            f.write("view structure\n")
            f.write("view wave\n")
            f.write("\n")
            f.write("add wave -noupdate -divider {GAIN}\n")
            f.write("add wave -noupdate -expand  -group GAIN\n")
            f.write("add wave -noupdate -group GAIN -radix bin {clk}\n")
            f.write("add wave -noupdate -group GAIN -radix bin {rst}\n")
            f.write("add wave -noupdate -group GAIN -radix dec {signal_in}\n")
            f.write("add wave -noupdate -group GAIN -radix dec {gain_in}\n")
            f.write("add wave -noupdate -group GAIN -radix dec {f1}\n")
            f.write("add wave -noupdate -group GAIN -color \"yellow\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {f1_scaled_sine_out}\n")
            f.write("add wave -noupdate -group GAIN -color \"yellow\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {result}\n")
            f.write("add wave -noupdate -group GAIN -radix dec {product}\n")
            f.write("add wave -noupdate -group GAIN -radix dec {result}\n")
            f.write(" \n")
            f.write("force -freeze clk 1 0, 0 {" + str(haf_clk_period) +  " ns} -r " + str(clk_period) + "\n")
            f.write("force -freeze rst 1 0\n")
            f.write("force -freeze rst 0 100\n")
            f.write("\n")
            f.write("force -freeze f1 10#21500000 0 \n")
            f.write("\n")
            f.write("#force -freeze signal_in 16#FC18 1000\n")
            f.write("#force -freeze gain_in 10#2048    1000\n")
            f.write("radix signed dec\n")
            f.write("\n")
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
            f.write("configure wave -childrowmargin 2\n")    
            f.write("#Run for 130 ns\n")
            f.write("run 20000\n")

            f.write("wave zoom full\n")

    def get_required_bits(self, number):
        if number == 0:
            return 1

        bits = math.ceil(math.log2(abs(number) + 1)) + 1
        return bits

    def raise_error(self, error):
        line_no = traceback.extract_stack()[0].linno
        raise ValueError(error + " at " + str(line_no))


    



        