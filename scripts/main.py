#!.venv/bin/python

#import main libs
import time
import psutil
import subprocess
import logging
from os.path import exists
from datetime import datetime, timedelta
from numpy import nanmean as npmean
from rich.console import Console
from pathlib import Path, PurePath
from dataclasses import dataclass, field

#Import support files
import support
from support import logger, console, get_time, start_time

################################# Timing Func ####################################
def log_time(fn):
    """Decorator timing function.  Accepts any function and returns a logging
    statement with the amount of time it took to run. DJ, I use this code everywhere still.  Thank you bud!

    Args:
        fn (function): Input function you want to time
    """	
    def inner(*args, **kwargs):
        tnow = time.time()
        out = fn(*args, **kwargs)
        te = time.time()
        took = round(te - tnow, 2)
        if took <= 60:
            logger.info(f"{fn.__name__} ran in {took:.3f}s")
        elif took <= 3600:
            logger.info(f"{fn.__name__} ran in {(took)/60:.3f}m")		
        else:
            logger.info(f"{fn.__name__} ran in {(took)/3600:.3f}h")
        return out
    return inner

################################# Sensor Functions ####################################
def get_cpu_temps():
    """Retrieves CPU stats.  

what about a dot matrix that has a heatmap representation of cpu temp
    """    
    #For Linux
    #Below doesn't work currently, but probably because they're vCPU's
    temps = psutil.sensors_temperatures(fahrenheit=True)
    if not temps:
        return "No CPU temperature found"
    elif "coretemp" in temps:
        avg_temp = npmean([temps["coretemp"][core].current for core in range(len(temps["coretemp"])) if "Core" in temps["coretemp"][core].label])

        return f"{avg_temp:.2f}"
    
    #Old Code
    # result = subprocess.run(
    #     ['sensors', '--query-cpu=power.draw,power.limit,temperature.gpu,utilization.gpu,fan.speed', '--format=csv,noheader,nounits'],
    #     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    # )
    # if result.returncode != 0:
    #     raise Exception(result.stderr)
#    try:
#         test_names = subprocess.check_output(["sensors"])
#     except Exception as e:
#         return e

def get_battery() -> float:
    """Calculates battery percentage.

    Returns:
        float: % battery 
    """    
    return psutil.sensors_battery()
    
def get_cpu_load(cc:int) -> tuple:
    """Calculates the average CPU load on the system at 1, 5, and 15 minute intervals
    Args:
        cc (int): Core count used in evaluating % Avg Load

    Returns:
        list: % load average of each time period
    """    
    avgs = psutil.getloadavg()
    numcores = cc
    if numcores > 1:
        percs = [x / numcores * 100 for x in avgs]
        return percs
    else:
        return avgs

def get_cpu_utilization() -> float:
    """Calculates CPU utlization percentage

    Returns:
        float: percentage of CPU being used
    """    
    return psutil.cpu_percent()
    
def get_core_count() -> int:
    """Counts the amount of CPU cores

    Returns:
        int: Number of cores
    """    
    return psutil.cpu_count()

def get_swap() -> object:
    """Calculates Swap file percentage used

    Returns:
        object: object of SWAP file being used
    """    
    return psutil.swap_memory()

def get_ram_utilization() -> object:
    """Calculates RAM percentage used

    Returns:
        object: object of RAM being used
    """
    return psutil.virtual_memory()

def get_gpu_info() -> dict:
    """Extracts GPU power draw, power limit, temperature, utilization, and fan speed

    Raises:
        Exception: Raise exception when GPU data unavailable

    Returns:
        temp_dict (dict): Dictionary of each GPU's information.  Indexed by numerical order
    """    
    try:
        result = subprocess.run(
            ['nvidia-smi', 
            '--query-gpu=power.draw,power.limit,temperature.gpu,utilization.gpu,memory.used,memory.total,fan.speed,index', 
            '--format=csv,noheader,nounits'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
            raise Exception(result.stderr)
        
        # Parse the gpu output (draw, totalpower, temperature, utilization, fan speed)
        results = result.stdout.split("\n")[:-1]
        temp_dict = {}
        for res in results:
            items = res.split(", ")
            gpu_draw, gpu_tpow, gpu_temp, gpu_utilization, gpu_mem_used, gpu_mem_total, gpu_fan_speed, idx = items[0], items[1], items[2], items[3], items[4], items[5], items[6], items[7]
            temp_dict[idx] = {
                "gpu_temp"       : gpu_temp,        # °C
                "gpu_utilization": gpu_utilization, # % 
                "gpu_fan_speed"  : gpu_fan_speed,   # rpms
                "gpu_mem_used"   : gpu_mem_used,    # GB
                "gpu_mem_total"  : gpu_mem_total,   # GB
                "gpu_draw"       : gpu_draw,        # W
                "gpu_power"      : gpu_tpow,        # W
            }
        if temp_dict:
            return temp_dict
        else:
            return "GPU info not found"
        
    except FileNotFoundError:
        return "nvidia-smi command not found. Is the NVIDIA driver installed?"
    #Query Hints
    #https://enterprise-support.nvidia.com/s/article/Useful-nvidia-smi-Queries-2

#Define dataclass container
@dataclass
class Timepoint():
    id         : datetime = None
    battery    : float = None
    core_count : int = None
    cpu_temp   : float = None
    cpu_util   : float = None
    cpu_1_min  : float = None
    cpu_5_min  : float = None
    cpu_15_min : float = None
    swap_util  : float = None
    ram_free   : float = None
    ram_util   : float = None
    ram_total  : float = None
    gpu_info   : dict = field(default_factory=lambda:{})


def sensor_town() -> dataclass:
    """Main extraction function.

    Returns:
        tp (dataclass): Populated Timepoint dataclass
    """    
    id       = get_time()
    # battery  = get_battery()
    cc       = get_core_count()
    cpu_info = get_cpu_load(cc)
    cpu_temp = get_cpu_temps()
    cpu_util = get_cpu_utilization()
    ram_info = get_ram_utilization()
    swap     = get_swap()
    g_info   = get_gpu_info()
    
    try:
        tp = Timepoint()
        tp.id = id
        tp.core_count = f"{cc}"
        tp.cpu_temp   = f"{cpu_temp}"                        # °C
        tp.cpu_util   = f"{cpu_util:.2f}"                    # %
        tp.cpu_1_min  = f"{cpu_info[0]:.2f}"                 # %
        tp.cpu_5_min  = f"{cpu_info[1]:.2f}"                 # %
        tp.cpu_15_min = f"{cpu_info[2]:.2f}"                 # %
        tp.swap_util  = f"{swap.percent:.2f}"                # %
        tp.ram_util   = f"{ram_info.percent:.2f}"            # %
        tp.ram_free   = f"{ram_info.free/1_000_000_000:.2f}" # GB
        tp.ram_total  = f"{ram_info.total/1_000_000_000:.2f}"# GB
        if isinstance(g_info, str):
            tp.gpu_info = g_info
        else:
            tp.gpu_info   = {**g_info}
            
        return tp
    
    except Exception as e:
        logger.warning(f"{e}")
        return None
    
################################# Main Function ####################################    
@log_time
def main():
    #Path Setup
    cdate = start_time.split("_")[0]
    fp = f"./data/json/{cdate}.json"
    # Check for historical data
    if exists(fp):
        jsondata = support.load_historical(fp)
        logger.info("JSON data loaded")
    else:
        jsondata = {}
        logger.warning("No historical data found")

    #Query sensors, fill timepoint dataclass
    tp = sensor_town()

    #If data found, save it, otherwise log an error
    if tp:
        support.save_data(tp, cdate, jsondata)
        logger.info("all sensors successfully queried")
    else:
        logger.warning("Retrieval malfunction.  Check logs")

if __name__ == '__main__':
    main()
