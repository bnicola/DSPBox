import traceback
import math
import matplotlib.pyplot as plt
import numpy as np
from  project_dsp import  *

class fir_module:

    def __init__(self, fir_type, instance_name, fs, fstart, fstop, in_width, coeff_width, numofCoeffs):
        if fir_type is None:
            self.raise_error(self, "Missing FIR type in module")
        if instance_name is None:
            self.raise_error(self, "Missing instance_name in module")
        if fs is None:
            self.raise_error(self, "Missing fs in module")
        if fstart is None:
            self.raise_error(self, "Missing fstart in module")
        if fstop is None:
            self.raise_error(self, "Missing fstop in module")
        if in_width is None:
            self.raise_error(self, "Missing in_width in module")
        if coeff_width is None:
            self.raise_error(self, "Missing coeff_width in module")
        if numofCoeffs is None:
            self.raise_error(self, "Missing numofCoeffs in module")

        if (fir_type != "LPF" and fir_type != "HPF" and fir_type != "BPF" and fir_type != "BSF"):
            raise ValueError("Please provide an FIR type(LPF, BPF , HPF or BSF)") 
        
        self.instance_name   = instance_name
        self.fs              = fs
        self.fstart          = fstart
        self.fstop           = fstop     
        self.in_width        = in_width
        self.coeff_width     = coeff_width
        self.numofCoeffs     = numofCoeffs

        if self.numofCoeffs % 2 == 0:  # Check if the number of coeff is even(we need an odd number of coeffs)
            self.numofCoeffs = self.numofCoeffs + 1

        # if (fir_type == 'HPF'):
        #      self.fstop = self.fs/2
        # elif (fir_type == 'LPF'):
        #     self.start  = 0 
        
        self.generate()
        add_file_to_list("fir_" + self.instance_name + ".v")
        d = debug()
        if (d):
            self.unit_test()
        

    def generate(self):
        print("...generating FIR with name " + self.instance_name + "...")
         # Calculate the scaling factor for the fixed-point representation
        hex_coeff = []
        nibbles = math.ceil(self.coeff_width/4)
        coeff = self.calculate_coefficients(self.fstart, self.fstop - self.fstart, self.fs, self.numofCoeffs)
        while all(element == 0 for element in coeff):
            self.numofCoeffs += 2
            coeff = self.calculate_coefficients(self.fstart, self.fstop - self.fstart, self.fs, self.numofCoeffs)

        for i in range(len(coeff)):
            if coeff[i] < 0:
                fraction_bits = (2**self.coeff_width) - 1 # the -1 is because the MSB is a sign bit
                fixed_coeff_i = (fraction_bits) - (round(-coeff[i] * (2**(self.coeff_width - 1)))) + 1
            elif coeff[i] > 0:
                fixed_coeff_i = round(coeff[i] * (2**(self.coeff_width - 1)))
            else:
                fixed_coeff_i = 0

            hex_coeff_i = hex(fixed_coeff_i)
            hex_coeff.append(hex_coeff_i)
        with open(proj_name() + "fir_" + self.instance_name + ".v", 'w') as f:
            f.write("module fir#\n")
            f.write("(\n")
            f.write("//------------------------------------------------------\n")
            f.write("//--	             External Parameters	               --\n")
            f.write("//------------------------------------------------------\n")
            f.write("parameter integer SIGNAL_WIDTH              = " + str(self.in_width) + ",   // Our wave signal bit width.\n")
            f.write("parameter integer NUM_OF_TAPS               = " + str(len(hex_coeff)) + ",  // The number of TAPS of our FIR.\n")
            f.write("parameter integer OUTOUT_SIGNAL_WIDTH       = " + str(self.in_width) + ",   // Our output bit size.\n")
            f.write("parameter integer COEFF_WIDTH               = " + str(self.coeff_width) + "    // Our Coeffs bit size.\n")
            f.write(")\n")
            f.write("(\n")
            f.write("    input clk,\n")
            f.write("    input reset,\n")
            f.write("    input signed [SIGNAL_WIDTH - 1:0] sig_in,\n")
            f.write("    output reg signed [SIGNAL_WIDTH - 1:0] sig_out\n")
            f.write(");\n")
            f.write("\n")
            f.write("    reg signed [(SIGNAL_WIDTH + 1) - 1:0] delay_line [0:NUM_OF_TAPS - 1];\n")
            f.write("    reg signed [COEFF_WIDTH - 1:0] coeffs [0:NUM_OF_TAPS - 1];\n")
            f.write("    wire signed [COEFF_WIDTH + SIGNAL_WIDTH - 1:0] accum[0:NUM_OF_TAPS - 1];\n")
            f.write("\n")    
            f.write("    integer i;\n")
            f.write("    \n")
            f.write("    // Initialize coefficients\n")
            f.write("    always @(posedge clk or posedge reset) begin\n")
            f.write("        if (reset) begin\n")
            index = 0
            for hex_i in hex_coeff:
                f.write("            coeffs[" + str(index) + "]  <= " + str(self.coeff_width) + "\'h")
                f.writelines(hex_i[2:].zfill(nibbles) + ';\n')
                index += 1  
            f.write("        end\n")
            f.write("    end\n\n")
            if (debug()):
                f.write("    wire signed [SIGNAL_WIDTH - 1:0] f1_sine;\n")
                f.write("    wire signed [SIGNAL_WIDTH - 1:0] f1_cos;\n")
                f.write("    wire signed [SIGNAL_WIDTH - 1:0] f1_scaled_sine_out;\n")
                f.write("\n")
                f.write("    wire [31:0] f1;\n")
                f.write("\n")
                f.write("    nco #(SIGNAL_WIDTH) input_signal_1  (\n")
                f.write("    .clk(clk), \n")
                f.write("    .rst(reset),\n") 
                f.write("    .freq_in(f1),\n")
                f.write("    .scale_factor(14745), \n")
                f.write("    .phase(0), \n")
                f.write("    .sine_out(f1_sine),\n")
                f.write("    .cos_out(f1_cos),\n")
                f.write("    .scaled_sine_out(f1_scaled_sine_out)\n")
                f.write("    );\n")
                f.write(" \n")   
            f.write("    always @(posedge clk, posedge reset) begin\n")
            f.write("    if (reset) begin\n")
            f.write("        for (i = 0; i < NUM_OF_TAPS - 1; i = i + 1) begin\n")
            f.write("            delay_line[i] <= 0;\n")
            f.write("            sig_out <= 0;\n")
            f.write("        end\n")
            f.write("    end else begin\n")
            accum_index = 0
            for i in range(0, len(hex_coeff)-1):
                f.write("        delay_line[" + str(i) + "] <= accum[" + str(i) + "];\n")
                
            f.write("        end\n")
            f.write("    end\n")
            f.write(" \n")  
            if (debug()):
                f.write("    assign accum[0] = ($signed(coeffs[0] * $signed(f1_scaled_sine_out)) >>> (COEFF_WIDTH - 1)) + 16'h0;\n")
                for i in range (1, len(hex_coeff)):
                    f.write("    assign accum[" + str(i) + "] = (($signed(coeffs[" + str(i) + "]) * $signed(f1_scaled_sine_out)) >>> (COEFF_WIDTH - 1)) + delay_line[" + str(i - 1) + "];\n")
                    accum_index = i
            else:
                f.write("    assign accum[0] = ($signed(coeffs[0] * $signed(sig_in)) >>> (COEFF_WIDTH - 1)) + 16'h0;\n")
                for i in range (1, len(hex_coeff)):
                    f.write("    assign accum[" + str(i) + "] = (($signed(coeffs[" + str(i) + "]) * $signed(sig_in)) >>> (COEFF_WIDTH - 1)) + delay_line[" + str(i - 1) + "];\n")
                    accum_index = i

            f.write("    assign sig_out = accum[" + str(accum_index) + "];\n")
            f.write(" \n")   
            f.write("endmodule\n")

            print("Done generating FIR " + "fir_" + self.instance_name + ".v\n")

    def apply_hamming_window(self, coefficients):
        N = len(coefficients)
        hamming_window = [0.54 - 0.46 * math.cos(2 * math.pi * n / (N - 1)) for n in range(N)]
        return [coefficients[n] * hamming_window[n] for n in range(N)]

    def calculate_coefficients(self, start_band, pass_band_width, fs, numCoefs):
        coefficients_ = []
        N = numCoefs
        frequency_resolution = self.fs / N
        
        #print("Generated " + str(N) + " Coefficients")
        start_band     = start_band / frequency_resolution # start at startBand Hz
        pass_band_width = pass_band_width / frequency_resolution #stop at (startBand + passBandWidth)  kHz

        hm_ = [0] * N
        # we create the unity frequency responses starting from start band for the width.
        # Note it will give us any type of filter LP, BP, HP...etc
        for i in range(N):
            if ((i >= start_band) and (i <= (start_band + pass_band_width - 1))) or ((i >= (N - start_band - pass_band_width)) and (i < (N - start_band))):
                hm_[i] = 1
            else:
                hm_[i] = 0

        # hm_ = apply_hamming_window(hm_)
        # h[n] = 1 in passed freq and 0 otherwise
        #
        #
        # ----------------                                   ------------------  
        #                 |                                  |
        #                 |                                  |
        #                 |                                  |
        # --------------------------------------------------------------------->fs
        #               cutoff                             N-cutoff
        #define 2D array first
        factor = [[0] * N for _ in range(N)]
        # Now build cosins where the hm_ = 1
        for m in range(N):
            for i in range(N):
                factor[m][i] = math.cos(2 * math.pi * m * i / N) * hm_[m]

        for i in range(N):
            coefficients_.append(0)

        # This is litterally a IDFT process. a bit of hack ;)
        for i in range(N):
            for j in range(N):
                coefficients_[i] += (factor[j][i])

        normalize_factor = coefficients_[0]

        for i in range(N):
            coefficients_[i] = coefficients_[i] / N

        index = 0
        half_way = (int(math.floor((N - 1)/2)))
        coeff = []
        for i in range(half_way + 1, N):
            coeff.append(coefficients_[i])
            index = index + 1
        for i in range(math.floor((N - 1)/2) + 1):
            coeff.append(coefficients_[i])
            index = index + 1
        windowed_coeff = self.apply_hamming_window(coeff)
    
        return windowed_coeff
    
    def unit_test(self):
        MHz = 1000000
        freq = [0.1, 0.2, 0.4, 0.6, 0.8, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5]
        clk = self.fs
        clk_period = int((1/clk) * 1e9) 
        haf_clk_period = int(clk_period / 2)
        with open(proj_name() + "fir_" + self.instance_name + ".do", 'w') as f:
            f.write("project compileall\n")
            f.write("vsim -gui work.fir -t ns\n")
            f.write("restart -f\n")
            f.write("view structure\n")
            f.write("view wave\n")
            f.write("    \n")
            f.write("add wave -noupdate -divider {FIR}\n")
            f.write("add wave -noupdate -expand  -group FIR\n")
            f.write("add wave -noupdate -group FIR -radix hex {clk}\n")
            f.write("add wave -noupdate -group FIR -radix hex {reset}\n")
            f.write("add wave -noupdate -group FIR -radix dec {sig_in}\n")
            f.write("add wave -noupdate -group FIR -radix dec {sig_out}\n")
            f.write("add wave -noupdate -group FIR -radix dec {delay_line}\n")
            f.write("add wave -noupdate -group FIR -radix dec {coeffs}\n")
            f.write("add wave -noupdate -group FIR -radix dec {accum}\n")
            f.write("add wave -noupdate -group FIR -color \"yellow\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {f1_scaled_sine_out}\n")
            f.write("add wave -noupdate -group FIR -color \"magenta\" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {sig_out}\n")
            f.write("\n")
            f.write("force -freeze clk 1 0, 0 {" + str(haf_clk_period) +  " ns} -r " + str(clk_period) + "\n")

            f.write("force -freeze reset 1 0\n")
            f.write("force -freeze reset 0 100\n")
            ind = 0
            time = 0

            for frq in freq:
                fr = int(math.ceil((2**32/clk)) * (frq * MHz))
                f.write("force -freeze f1 10#" + str(fr) + " " + str(time) + " \n")
                time = time + 5000

            f.write("\n")
            f.write("radix signed dec\n")
            f.write("\n")
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
            f.write("configure wave -childrowmargin 2 \n")   
            f.write("#Run for 130 ns\n")
            f.write("run " + str(time + 5000) + "\n")
            f.write("wave zoom full\n")

    def raise_error(self, error):
        line_no = traceback.extract_stack()[0].linno
        raise ValueError(error + " at " + str(line_no))


    



        