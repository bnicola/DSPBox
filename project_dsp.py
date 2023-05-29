import traceback 
import os
import shutil
import argparse

RED = '\033[91m'
RESET = '\033[0m'

project_name = ""
debugging = False
file_list = []

def set_debug(dbg):
    global debugging
    debugging = dbg

def debug():
    global debugging
    return debugging

def set_proj_name(proj_name):
    global project_name
    global file_list
    if proj_name == "":
        line_no = traceback.extract_stack()[0].lineno
        raise ValueError("Must provide project name at " + str(line_no))
    project_name = proj_name
    if not os.path.exists(project_name):
        # Create the directory
        os.mkdir(project_name)
    curr_proj_path = os.getcwd() + "/" + project_name

    shutil.copy2("dsp_proj.mpf", curr_proj_path)
    shutil.copy2("nco.v", curr_proj_path)
    

def proj_name():
    if project_name == "":
        line_no = traceback.extract_stack()[0].lineno
        raise ValueError("No project name set " + str(line_no))
    return project_name + "/"

def modify_proj_file(proj_path, proj_filename, verilog_files_list): 

    with open(proj_filename, 'r') as file:
        lines = file.readlines()

    found_target = False
    for i, line in enumerate(lines):
        if 'Project_SortMethod = unused' in line:
            found_target = True
            break
    
    if found_target:
        lines[i+1] = 'Project_Files_Count = ' + str(len(verilog_files_list) + 1) + '\n'
        lines.insert(i+2, 'Project_File_0 = ' + proj_path +'/nco.v\n')
        lines.insert(i+3, 'Project_File_P_0 = cover_toggle 0 file_type verilog group_id 0 cover_exttoggle 0 cover_nofec 0 cover_cond 0 vlog_1995compat 0 vlog_nodebug 0 last_compile 1685062041 cover_fsm 0 cover_branch 0 vlog_noload 0 folder {Top Level} cover_excludedefault 0 vlog_enable0In 0 vlog_disableopt 0 cover_covercells 0 voptflow 1 vlog_showsource 0 vlog_hazard 0 cover_optlevel 3 toggle - vlog_0InOptions {} ood 1 cover_noshort 0 vlog_upper 0 compile_to work vlog_options {} compile_order 0 cover_expr 0 dont_compile 0 cover_stmt 0\n')
        index = 4
        filex = 1
        for module in verilog_files_list:
            lines.insert(i+index, 'Project_File_' + str(filex) + '= ' + proj_path + '/' + module + '\n')
            index += 1
            lines.insert(i+index, 'Project_File_P_' + str(filex) + ' = cover_toggle 0 file_type verilog group_id 0 cover_exttoggle 0 cover_nofec 0 cover_cond 0 vlog_1995compat 0 vlog_nodebug 0 last_compile 1685062041 cover_fsm 0 cover_branch 0 vlog_noload 0 folder {Top Level} cover_excludedefault 0 vlog_enable0In 0 vlog_disableopt 0 cover_covercells 0 voptflow 1 vlog_showsource 0 vlog_hazard 0 cover_optlevel 3 toggle - vlog_0InOptions {} ood 1 cover_noshort 0 vlog_upper 0 compile_to work vlog_options {} compile_order 0 cover_expr 0 dont_compile 0 cover_stmt 0\n')
            index += 1
            filex += 1

        with open(proj_filename, 'w') as file:
            file.writelines(lines)

def add_file_to_list(file):
    file_list.append(file)

def finalise_project():
    curr_proj_path = os.getcwd() + "/" + project_name
    modify_proj_file(curr_proj_path, curr_proj_path + "/dsp_proj.mpf", file_list)

def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    