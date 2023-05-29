import traceback
import numpy as np
import math
from  project_dsp import  *

class mixer:

    def __init__(self, instance_name, fs, signal_width, mixing_signal_width, out_width):
        
        if instance_name is None:
            self.raise_error(self, "Missing instance_name in module")
        if fs is None:
            self.raise_error(self, "Missing fs in module")
        if signal_width is None:
            self.raise_error(self, "Missing signal_width in module")
        if mixing_signal_width is None:
            self.raise_error(self, "Missing mixing_signal_width in module")
        if out_width is None:
            self.raise_error(self, "Missing out_width in module")
       
        self.instance_name        = instance_name
        self.fs                   = fs
        self.signal_width         = signal_width
        self.mixing_signal_width  = mixing_signal_width
        self.out_width            = out_width 
        
        d = debug()
        if (d == True):
            self.unit_test()
        self.generate()
        add_file_to_list("mixer_" + self.instance_name + ".v")
        

    def generate(self):
        print("...generating Mixer with name " + self.instance_name + "...")
        with open(proj_name() + "mixer_" + self.instance_name + ".v", 'w') as f:
            f.write("module mixer_" + self.instance_name + " #\n")
            f.write("(\n")
            f.write("//------------------------------------------------------\n")
            f.write("//--	             External Parameters	           --\n")
            f.write("//------------------------------------------------------\n")
            f.write("parameter integer SIGNAL_WIDTH              = " + str(self.signal_width) + ",   // Our wave signal bit width\n")
            f.write("parameter integer MIXING_SIGNAL_WIDTH       = " + str(self.mixing_signal_width) + ",   // Our mixing LO signal bit width.\n")
            f.write("parameter integer OUTOUT_SIGNAL_WIDTH       = " + str(self.out_width) + "    // Our output bit size\n")
            f.write(")\n")
            f.write("(\n")
            f.write("//-------------------------------------------------------\n")
            f.write("//--	             Ports                              --\n")
            f.write("//-------------------------------------------------------\n")
            f.write("    input clk, rst,\n")
            f.write("    input signed  [SIGNAL_WIDTH - 1 : 0]        sig,\n")
            f.write("    input signed  [MIXING_SIGNAL_WIDTH - 1 : 0] lo,\n")
            f.write("    output signed [OUTOUT_SIGNAL_WIDTH - 1 : 0] mixed\n")
            f.write(");\n\n")
            f.write("    reg signed [SIGNAL_WIDTH + MIXING_SIGNAL_WIDTH - 1: 0] mult;\n")

            f.write("    wire signed [SIGNAL_WIDTH - 1:0] f1_sine;\n")
            f.write("    wire signed [SIGNAL_WIDTH - 1:0] f1_cos;\n")
            f.write("    wire signed [SIGNAL_WIDTH - 1:0] f1_scaled_sine_out;\n")

            f.write("    wire signed [MIXING_SIGNAL_WIDTH - 1:0] f2_sine;\n")
            f.write("    wire signed [MIXING_SIGNAL_WIDTH - 1:0] f2_cos;\n")
            f.write("    wire signed [MIXING_SIGNAL_WIDTH - 1:0] f2_scaled_sine_out;\n\n")
            
            if (debug()):
                f.write("    wire [31:0] f1;\n")
                f.write("    wire [31:0] f2;\n\n")

                f.write("    nco #(SIGNAL_WIDTH) input_signal_1  (\n")
                f.write("    .clk(clk), \n")
                f.write("    .rst(rst), \n")
                f.write("    .freq_in(f1),\n")
                f.write("    .scale_factor(8190), \n")
                f.write("    .phase(0), \n")
                f.write("    .sine_out(f1_sine), \n")
                f.write("    .cos_out(f1_cos),\n")
                f.write("    .scaled_sine_out(f1_scaled_sine_out)\n")
                f.write("    );\n\n\n")


                f.write("    nco #(MIXING_SIGNAL_WIDTH)input_signal_2 (\n")
                f.write("    .clk(clk), \n")
                f.write("    .rst(rst), \n")
                f.write("    .freq_in(f2),\n")
                f.write("    .scale_factor(8190), \n")
                f.write("    .phase(0), \n")
                f.write("    .sine_out(f2_sine), \n")
                f.write("    .cos_out(f2_cos),\n")
                f.write("    .scaled_sine_out(f2_scaled_sine_out)\n")
                f.write("    );\n\n")

                f.write("    always @(posedge clk) begin \n")
                f.write("        if (rst) begin  \n")
                f.write("            mult <= 0;\n")
                f.write("        end\n")
                f.write("        else begin \n")
                f.write("            mult <= f1_sine * f2_sine; //sig * lo;\n")
                f.write("        end\n")
                f.write("    end\n\n")
                f.write("    assign mixed = mult >> (SIGNAL_WIDTH + MIXING_SIGNAL_WIDTH - OUTOUT_SIGNAL_WIDTH - 1);//mult[SIGNAL_WIDTH + MIXING_SIGNAL_WIDTH - 1 : SIGNAL_WIDTH + MIXING_SIGNAL_WIDTH - OUTOUT_SIGNAL_WIDTH + 1];\n\n")
            else:
                f.write("    always @(posedge clk) begin \n")
                f.write("        if (rst) begin  \n")
                f.write("            mult <= 0;\n")
                f.write("        end\n")
                f.write("        else begin \n")
                f.write("            mult <= sig * lo;\n")
                f.write("        end\n")
                f.write("    end\n\n")
                f.write("    assign mixed = mult >> (SIGNAL_WIDTH + MIXING_SIGNAL_WIDTH - OUTOUT_SIGNAL_WIDTH - 1);//mult[SIGNAL_WIDTH + MIXING_SIGNAL_WIDTH - 1 : SIGNAL_WIDTH + MIXING_SIGNAL_WIDTH - OUTOUT_SIGNAL_WIDTH + 1];\n\n")
            

            f.write("endmodule\n")

            print("Done generating MIXER " + "mixer_" + self.instance_name + ".v\n")

    
    def unit_test(self):
        MHz = 1000000
        clk = self.fs
        clk_period = int((1/clk) * 1e9) 
        haf_clk_period = int(clk_period / 2)
        with open(proj_name() + "mixer_" + self.instance_name + ".do", 'w') as f:  
            f.write("project compileall\n")
            f.write("vsim -gui work.mixer_" + self.instance_name + " -t ns\n")
            f.write("restart -f\n")
            f.write("view structure\n")
            f.write("view wave\n\n")
            
            f.write("add wave -noupdate -divider {mixer}\n")
            f.write("add wave -noupdate -expand  -group mixer\n")
            f.write("add wave -noupdate -group mixer -radix hex {clk}\n")
            f.write("add wave -noupdate -group mixer -radix hex {rst}\n")
            f.write("add wave -noupdate -group mixer -color \"yellow\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {f1_sine}\n")
            f.write("add wave -noupdate -group mixer -color \"magenta\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {f2_sine}\n")
            f.write("add wave -noupdate -group mixer -color \"magenta\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {mixed}\n\n")
           
            f.write("force -freeze clk 1 0, 0 {" + str(haf_clk_period) +  " ns} -r " + str(clk_period) + "\n")

            f.write("force -freeze rst 1 0\n")
            f.write("force -freeze rst 0 100\n\n")

            f.write("force -freeze f1 10#42949673 0 \n")
            f.write("force -freeze f2 10#2147483 0 \n\n")

            f.write("radix signed dec\n")

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
            f.write("configure wave -childrowmargin 2 \n")
            f.write("run 36000\n")
            f.write("wave zoom full\n")


    



        