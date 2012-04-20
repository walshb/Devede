import sys

import devede_other

def get_number(line):
    pos=line.find(":")
    if pos==-1:
        return -1

    return int(line[pos+1:])

def get_cores():

    """ Returns the number of cores available in the system """
    if (sys.platform=="win32") or (sys.platform=="win64"):
        logical_cores = win32api.GetSystemInfo()[5] #Logical Cores
        return logical_cores

    failed=False
    try:
        proc=open("/proc/cpuinfo","r")
    except:
        failed=True


    if failed:
        # If can't read /proc/cpuinfo, try to use the multiprocessing module
        try:
            import multiprocessing
            return multiprocessing.cpu_count()
        except:
            pass
        return 1 # if we can't open /PROC/CPUINFO, return only one CPU (just in case)

    siblings=1 # default values
    cpu_cores=1 # for siblings and cpu cores
    notfirst=False
    ncores=0
    while(True):
        line=proc.readline()

        if (((line[:9]=="processor") and notfirst) or (line=="")):

            # each entry is equivalent to CPU_CORES/SIBLINGS real cores
            # (always 1 except in HyperThreading systems, where it counts 1/2)

            ncores+=(float(cpu_cores))/(float(siblings))
            siblings=1
            cpu_cores=1

        if line=="":
            break

        if line[:9]=="processor":
            notfirst=True
        elif (line[:8]=="siblings"):
            siblings=get_number(line)
        elif (line[:9]=="cpu cores"):
            cpu_cores=get_number(line)

    if(ncores<=1.0):
        return 1
    else:
        return int(ncores)


def get_default_globals(pic_path, help_path, glade=None):
    global_vars = {}

    global_vars["PAL"]=True
    global_vars["disctocreate"]=""
    global_vars["path"]=pic_path
    global_vars["install_path"]=pic_path
    global_vars["menu_widescreen"]=False
    global_vars["gladefile"]=glade
    global_vars["erase_temporary_files"]=True
    global_vars["number_actions"]=1
    global_vars["expand_advanced"]=False
    global_vars["erase_files"]=True
    global_vars["action_todo"]=2
    global_vars["filmpath"]=""
    global_vars["help_path"]=help_path
    global_vars["finalfolder"]=""
    global_vars["sub_codepage"]="ISO-8859-1"
    global_vars["sub_language"]="EN (ENGLISH)"
    global_vars["with_menu"]=True
    global_vars["AC3_fix"]=False
    global_vars["cores"]=get_cores()
    global_vars["use_ffmpeg"]=False
    global_vars["warning_ffmpeg"]=True
    global_vars["shutdown_after_disc"]=False

    global_vars["menu_top_margin"]=0.125
    global_vars["menu_bottom_margin"]=0.125
    global_vars["menu_left_margin"]=0.1
    global_vars["menu_right_margin"]=0.1

    global_vars['multicore'] = 1

    return global_vars


def check_programs(global_vars):
    errors="" # check for installed programs
    if (sys.platform=="win32") or (sys.platform=="win64"):
        try:
            devede_other.check_program(["mplayer.exe", "-v"])
        except:
            errors+="mplayer\n"
        try:
            devede_other.check_program(["mencoder.exe", "-msglevel", "help"])
        except:
            errors+="mencoder\n"
        try:
            devede_other.check_program(["dvdauthor.exe", "--help"])
        except:
            errors+="dvdauthor\n"
        try:
            devede_other.check_program(["vcdimager.exe", "--help"])
        except:
            errors+="vcdimager\n"
        try:
            devede_other.check_program(["iconv.exe", "--help"])
        except:
            errors+="iconv\n"

        try:
            devede_other.check_program(["mkisofs.exe"])
            mkisofs=True
            global_vars["iso_creator"]="mkisofs.exe"
        except:
            try:
                devede_other.check_program(["genisoimage.exe"])
                global_vars["iso_creator"]="genisoimage.exe"
            except:
                errors+="genisoimage/mkisofs\n"

        try:
            devede_other.check_program(["spumux.exe", "--help"])
        except:
            errors+="spumux\n"

    else:

        if 127==devede_other.check_program("mplayer -v"):
            errors+="mplayer\n"
        if 127==devede_other.check_program("mencoder -msglevel help"):
            errors+="mencoder\n"
        if 127==devede_other.check_program("ffmpeg --help"):
            errors+="ffmpeg\n"
        if 127==devede_other.check_program("dvdauthor --help"):
            errors+="dvdauthor\n"
        if 127==devede_other.check_program("vcdimager --help"):
            errors+="vcdimager\n"
        if 127==devede_other.check_program("iconv --help"):
            errors+="iconv\n"
        if 127==devede_other.check_program("mkisofs -help"):
            if 127==devede_other.check_program("genisoimage -help"):
                errors+="genisoimage/mkisofs\n"
            else:
                global_vars["iso_creator"]="genisoimage"
        else:
            global_vars["iso_creator"]="mkisofs"

        if 127==devede_other.check_program("spumux --help"):
            errors+="spumux\n"

    return errors

