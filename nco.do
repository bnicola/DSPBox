project compileall
vsim -gui work.nco -t ns
restart -f
view structure
view wave
 
add wave -noupdate -divider {nco}
add wave -noupdate -expand  -group nco
add wave -noupdate -group nco -radix hex {clk}
add wave -noupdate -group nco -radix hex {rst}
add wave -noupdate -group nco -radix dec {freq_in}
add wave -noupdate -group nco -radix dec {sine_out}
add wave -noupdate -group nco -radix dec {scaled_wave}
add wave -noupdate -group nco -color "yellow" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {sine_out}
add wave -noupdate -group nco -color "magenta" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {scaled_sine_out}
#add wave -noupdate -group nco -color "magenta" -format analog-step -height 200 -max 32768 -min -32768 -radix dec {scaled_wave}
add wave -noupdate -group nco -radix dec {current_phase}
add wave -noupdate -group nco -radix dec {scale_factor}
add wave -noupdate -group nco -radix dec {phase}
add wave -noupdate -group nco -radix dec {initial_phase}
add wave -noupdate -group nco -radix dec {phase_increment}
add wave -noupdate -group nco -radix dec {phase_accumulator}
add wave -noupdate -group nco -radix dec {sine_lut}
 
 
force -freeze sim:/clk 1 0, 0 {5 ns} -r 10
force -freeze sim:/freq_in 0 0

force -freeze sim:/rst 1 0
force -freeze sim:/rst 0 100
#20kHz 2^32*f/fs(where fs = clk = 100MHz)
#so for x Hz ==> 2^32 * x / 100MHz
force -freeze sim:/freq_in 10#858993 0 
#force -freeze sim:/freq_in 10#64424509 100000

#initial phase of 0
force -freeze phase 10#0 0

#14 bits fraction * 1.0
force -freeze sim:/scale_factor 10#16384 0 
#14 bits fraction * 0.5
force -freeze sim:/scale_factor 10#8196 40000 
#14 bits fraction * 0.25
force -freeze sim:/scale_factor 10#4096 120000 

WaveRestoreZoom {0 ns} {1000 ns}
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {130 ns}
configure wave -namecolwidth 212
configure wave -valuecolwidth 120
configure wave -justifyvalue left
configure wave -signalnamewidth 0
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2    
#Run for 130 ns
run 200000
wave zoom full
