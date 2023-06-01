
import traceback
import math
import matplotlib.pyplot as plt
import numpy as np
from  project_dsp import  *

class fm_modulator:

    def __init__(self, instance_name, fs, modulating_min_freq, modulating_max_freq, signal_width = 16, out_width=16):
        
        if instance_name is None:
            self.raise_error(self, "Missing instance_name in module")
        if fs is None:
            self.raise_error(self, "Missing fs in module")
        if modulating_min_freq is None:
            self.raise_error(self, "Missing modulating_min_freq in module")
        if modulating_max_freq is None:
            self.raise_error(self, "Missing modulating_max_freq in module")
        if signal_width is None:
            self.raise_error(self, "Missing signal_width in module")
        if out_width is None:
            self.raise_error(self, "Missing out_width in module")
       
        self.instance_name       = instance_name
        self.fs                  = fs
        self.modulating_min_freq = modulating_min_freq 
        self.modulating_max_freq = modulating_max_freq 
        self.out_width           = out_width   
        self.signal_width        = signal_width 

        d = debug()
        if (d == True):
            self.unit_test()
        self.generate()
        add_file_to_list("fm_modulator_" + self.instance_name + ".v")

    def generate(self):
        print("...generating FM Modulator with name " + self.instance_name + "...")
        with open(proj_name() + "fm_modulator_" + self.instance_name + ".v", 'w') as f:
            f.write("module fm_modulator_" + self.instance_name + " #\n")
            f.write("(\n")
            f.write("    parameter integer IN_SIG_WIDTH    = " + str(self.signal_width) + ",\n")
            f.write("    parameter integer FREQ_MIN        = " + str(self.modulating_min_freq) + ", //Hz\n")
            f.write("    parameter integer FREQ_MAX        = " + str(self.modulating_max_freq) + ",//Hz\n")
            f.write("    parameter integer RESULT_WIDTH    = " + str(self.out_width) + "\n")
            f.write(")\n")
            f.write("(\n")
            f.write("    input clk, rst,\n")
            f.write("    input signed [IN_SIG_WIDTH - 1:0] signal_in,\n")
            f.write("    output reg signed [RESULT_WIDTH - 1:0] result\n")
            f.write(");\n\n")
            if(debug()):
                f.write("wire signed [IN_SIG_WIDTH - 1:0] modulating_sig;\n")
            f.write("wire signed [IN_SIG_WIDTH - 1:0] modulated_sig;\n\n")

            f.write("reg [31:0] scaled_freq;\n")

            f.write("wire [31:0] modulating_freq;\n\n")

            f.write("reg [31:0] f_minimum;\n")
            f.write("reg [31:0] f_maximum;\n")
            f.write("reg [31:0] gain;\n")
            f.write("reg [31:0] offset;\n")

            f.write("// Formula for changing the frequecy of the nco according to iunput signal\n")
            f.write("//                (FREQ_MAX - FREQ_MIN)                    (FREQ_MAX + FREQ_MIN)\n")
            f.write("// NCO_Freq_In = ----------------------- x input_signal +  =---------------------\n")
            f.write("//                2^IN_SIG_WIDTH                                     2\n")
            f.write("parameter min  = (42.95 * FREQ_MIN);\n")
            f.write("parameter max  = (42.95 * FREQ_MAX);\n")
            f.write("parameter slope = ((max - min) / (2 * (2**(IN_SIG_WIDTH-1))));\n")
            f.write("parameter threshold = (max + min) / 2;\n")

            f.write("always @(posedge clk or posedge rst) begin\n")
            f.write("    if (rst) begin \n")
            f.write("        f_minimum <= 0;\n")
            f.write("        f_maximum <= 0;\n")
            f.write("        gain      <= 0;\n")
            f.write("        offset    <= 0;\n")
            f.write("        scaled_freq <= 0;\n")
            f.write("    end\n")
            f.write("    else begin \n")
            f.write("        f_minimum <= min; \n")
            f.write("        f_maximum <= max; \n")
            f.write("        gain      <= slope; \n")
            f.write("        offset    <= threshold; \n")
            if(debug()):
                f.write("        scaled_freq <= $signed(slope * modulating_sig) + $signed(threshold);\n")
            else:
                f.write("        scaled_freq <= $signed(slope * signal_in) + $signed(threshold);\n")
            f.write("    end\n")
            f.write("end\n\n")
            if(debug()):
                f.write("function_gen  #(IN_SIG_WIDTH) modulating_signal  (\n")
                f.write("    .clk(clk),\n")
                f.write("    .rst(rst), \n")
                f.write("    .freq_in(modulating_freq),\n")
                f.write("    .scale_factor(13'd8190),\n") 
                f.write("    .phase(13'd0), \n")
                f.write("    .wave_type(3'h1),\n")
                f.write("    .wave_out (modulating_sig) \n")
                f.write(");\n")
                
            f.write("nco #(IN_SIG_WIDTH) modulated_signal  (\n")
            f.write("    .clk(clk), \n")
            f.write("    .rst(rst), \n")
            f.write("    .freq_in(scaled_freq),\n")
            f.write("    .scale_factor(13'd8190),\n") 
            f.write("    .phase(13'd0), \n")
            f.write("    .sine_out(modulated_sig),\n") 
            f.write("    .cos_out(),\n")
            f.write("    .scaled_sine_out()\n")
            f.write(");\n\n")

            f.write("assign result = $signed(modulated_sig);\n")
            
            f.write("endmodule\n")


            print("Done generating FM_MODULATOR " + "fm_modulator_" + self.instance_name + ".v\n")

    
    def unit_test(self):
        MHz = 1000000
        clk = self.fs
        clk_period = int((1/clk) * 1e9) 
        haf_clk_period = int(clk_period / 2)
        with open(proj_name() + "fm_modulator_" + self.instance_name + ".do", 'w') as f:
            f.write("project compileall\n")
            f.write("vsim -gui work.fm_modulator_" + self.instance_name + " -t ns\n")
            f.write("restart -f\n")
            f.write("view structure\n")
            f.write("view wave\n\n")
                     
            f.write("add wave -noupdate -divider {FM_MODULATOR}\n")
            f.write("add wave -noupdate -expand  -group FM_MODULATOR\n")
            f.write("add wave -noupdate -group FM_MODULATOR -radix bin {clk}\n")
            f.write("add wave -noupdate -group FM_MODULATOR -radix bin {rst}\n")
            f.write("add wave -noupdate -group FM_MODULATOR -radix dec {signal_in}\n")
            f.write("add wave -noupdate -group FM_MODULATOR -radix dec {modulating_freq}\n")
            f.write("add wave -noupdate -group FM_MODULATOR -radix dec {scaled_freq}\n")
            f.write("add wave -noupdate -group FM_MODULATOR -color \"yellow\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {modulating_sig}\n")
            f.write("add wave -noupdate -group FM_MODULATOR -color \"magenta\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {modulated_sig}\n")
            f.write("add wave -noupdate -group FM_MODULATOR -radix dec {result}\n\n")
            
            f.write("force -freeze clk 1 0, 0 {5 ns} -r 10\n")
            f.write("force -freeze rst 1 0\n")
            f.write("force -freeze rst 0 100\n\n")

            f.write("force -freeze modulating_freq 10#429500 0 \n")

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
            f.write("run 140000\n")

            f.write("wave zoom full\n")


    def raise_error(self, error):
        line_no = traceback.extract_stack()[0].lineno
        raise ValueError(error + " at " + str(line_no))
    



        
            
