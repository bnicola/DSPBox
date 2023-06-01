import traceback
import math
import matplotlib.pyplot as plt
import numpy as np
from  project_dsp import  *

class diff:

    def __init__(self, instance_name, fs, signal_width=16, out_width=16):
        
        if instance_name is None:
            self.raise_error(self, "Missing instance_name in module")
       
        self.instance_name   = instance_name
        self.fs              = fs
        self.signal_width    = signal_width   
        self.out_width       = out_width 
    
        d = debug()
        if (d == True):
            self.unit_test()
        self.generate()
        add_file_to_list("diff_" + self.instance_name + ".v")

    def generate(self):
        print("...generating Diff with name " + self.instance_name + "...")
        with open(proj_name() + "diff_" + self.instance_name + ".v", 'w') as f:
            
            f.write("module diff_" + self.instance_name + "#\n")
            f.write("(\n")
            f.write("    parameter integer IN_SIG_WIDTH  = 16,\n")
            f.write("    parameter integer OUT_SIG_WIDTH = 16\n")
            f.write(")\n")
            f.write("(\n")
            f.write("    input clk, rst,\n")
            f.write("    input signed [IN_SIG_WIDTH - 1:0] signal_in,\n")
            f.write("    output reg signed [OUT_SIG_WIDTH - 1:0] signal_out\n")
            f.write(");\n\n")
            
            f.write("    reg signed [IN_SIG_WIDTH - 1 :0] delay;\n")
            if(debug()):
                f.write("    wire signed [IN_SIG_WIDTH - 1:0] f1_sine;\n")
                f.write("    wire signed [IN_SIG_WIDTH - 1:0] f1_cos;\n")
                f.write("    wire signed [IN_SIG_WIDTH - 1:0] f1_scaled_sine_out;\n")
                f.write("    wire [31:0] f1;\n")

                f.write("    nco #(IN_SIG_WIDTH) input_signal_1  (\n")
                f.write("        .clk(clk), \n")
                f.write("        .rst(rst), \n")
                f.write("        .freq_in(f1),\n")
                f.write("        .scale_factor(8190), \n")
                f.write("        .phase(0),\n") 
                f.write("        .sine_out(f1_sine), \n")
                f.write("        .cos_out(f1_cos),\n")
                f.write("        .scaled_sine_out(f1_scaled_sine_out)\n")
                f.write(");\n")

            f.write("    always @(posedge clk , posedge rst) begin\n")
            f.write("        if (rst) begin \n")
            f.write("            delay <= 0;\n")
            f.write("        end\n")
            f.write("        else begin \n")
            if(debug()):
                f.write("        delay <= f1_cos; \n")
            else:
                f.write("        delay <= signal_in;\n")
            f.write("        end\n")
            f.write("end\n\n")
            if(debug()):
                f.write("    assign signal_out = $signed(f1_cos - delay);\n\n")
            else:
                f.write("    assign signal_out = $signed(signal_in - delay);\n\n")
            
            f.write("endmodule\n")

            print("Done generating DIFF " + "dif_" + self.instance_name + ".v\n")
    
    def unit_test(self):
        MHz = 1000000
        clk = self.fs
        clk_period = int((1/clk) * 1e9) 
        haf_clk_period = int(clk_period / 2)
        with open(proj_name() + "diff_" + self.instance_name + ".do", 'w') as f:
            f.write("project compileall\n")
            f.write("vsim -gui work.diff_" + self.instance_name + " -t ns\n")
            f.write("restart -f\n")
            f.write("view structure\n")
            f.write("view wave\n\n")
            
            f.write("add wave -noupdate -divider {DIFF}\n")
            f.write("add wave -noupdate -expand  -group DIFF\n")
            f.write("add wave -noupdate -group DIFF -radix bin {clk}\n")
            f.write("add wave -noupdate -group DIFF -radix bin {rst}\n")
            f.write("add wave -noupdate -group DIFF -radix dec {signal_in}\n")
            f.write("add wave -noupdate -group DIFF -radix dec {signal_out}\n")
            f.write("add wave -noupdate -group DIFF -radix dec {f1}\n")
            f.write("add wave -noupdate -group DIFF -radix dec {delay}\n")
            f.write("add wave -noupdate -group DIFF -color \"yellow\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {f1_scaled_sine_out}\n")
            f.write("add wave -noupdate -group DIFF -color \"yellow\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {signal_out}\n")
            
            f.write("force -freeze clk 1 0, 0 {5 ns} -r 10\n")
            f.write("force -freeze rst 1 0\n")
            f.write("force -freeze rst 0 1000\n")

            f.write("force -freeze f1 10#21500000 0 \n")
            f.write("force -freeze f1 10#43000000 5000 \n")
            f.write("force -freeze f1 10#86000000 10000 \n")
            f.write("force -freeze f1 10#129000000 15000 \n")
            f.write("force -freeze f1 10#172000000 20000 \n")
            f.write("force -freeze f1 10#215000000 25000 \n")
            f.write("force -freeze f1 10#258000000 30000 \n")
            f.write("force -freeze f1 10#301000000 35000 \n")
            f.write("force -freeze f1 10#344000000 40000 \n")
            f.write("force -freeze f1 10#387000000 45000 \n")

            f.write("radix signed dec\n\n")

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
            f.write("run 55000\n")

            f.write("wave zoom full\n")
    
    def raise_error(self, error):
        line_no = traceback.extract_stack()[0].lineno
        raise ValueError(error + " at " + str(line_no))



    



        