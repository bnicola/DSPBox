import math
import traceback
import argparse

from  project_dsp import  *
from fir     import fir_module
from wavegen import wavegen
from mixer   import mixer
from gain    import gain
from gain_c  import gain_c
from diff    import diff
from fm_modulator import fm_modulator

def main():
    parser = argparse.ArgumentParser(description='Command Line Argument')

    # Add arguments
    parser.add_argument('-d', '--debugging', type=str_to_bool, default = True, help='Debug generation(used to generate modules that can be debugged)')
    parser.add_argument('-p', '--project', type=str, default = "DSP_Project", help='Specify project name')

    # Parse the command line arguments
    args = parser.parse_args()

    # Access the argument values
    debugging = args.debugging
    project_name = args.project
    set_debug(debugging)
    set_proj_name(project_name)
    print("Main debugging = " + str(debugging))
    # ------------------------------------------------------------------------------------------------
    fsampling = 100e6
    bpf = fir_module(fir_type      = "BPF",
                     instance_name = "bpf", 
                     fs            = fsampling, 
                     fstart        = 2e6, 
                     fstop         = 4e6, 
                     in_width      = 16, 
                     coeff_width   = 21, 
                     numofCoeffs   = 127)

    lpf = fir_module(fir_type      = "LPF",
                     instance_name = "lpf", 
                     fs            = fsampling, 
                     fstart        = 0, 
                     fstop         = 3e6, 
                     in_width      = 16, 
                     coeff_width   = 21, 
                     numofCoeffs   = 127)
    
    hpf = fir_module(fir_type      = "HPF",
                     instance_name = "hpf", 
                     fs            = fsampling, 
                     fstart        = 3e6, 
                     fstop         = -1, 
                     in_width      = 16, 
                     coeff_width   = 21, 
                     numofCoeffs   = 127)
    
    wgen = wavegen(instance_name = "lo", 
                   fs            = fsampling, 
                   freq          = 1e6,
                   init_phase    = 0, 
                   out_width     = 16)

    mix = mixer(instance_name       = "Mixer",
                fs                  = fsampling,
                signal_width        = 16,
                mixing_signal_width = 16,
                out_width           = 16)

    #in_gain = gain(instance_name = "input",
    #               fs            = fsampling,
    #               gain          = 1.5)
    
    in_gain2 = gain_c(instance_name = "input2",
                      fs            = fsampling
                      )
    
    d = diff (instance_name = "hp",
              fs            = fsampling
             )
    fm_m = fm_modulator(instance_name="test",
                        fs = fsampling,
                        modulating_min_freq=5000,
                        modulating_max_freq=1000000)
    

    finalise_project()


if __name__ == "__main__":
    main()