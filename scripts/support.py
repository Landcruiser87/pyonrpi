import os
import time
import json
import shutil
import logging
import datetime
import numpy as np
from os.path import exists
from dataclasses import dataclass
from pathlib import PurePath, Path
from rich.console import Console
from rich.logging import RichHandler

#CLASS Numpy encoder
class CustomEncoder(json.JSONEncoder):
    """Custom numpy JSON Encoder.  Takes in any type from an array and formats it to something that can be JSON serialized. Source Code found here. https://pynative.com/python-serialize-numpy-ndarray-into-json/
    Args:
        json (object): Json serialized format
    """	
    def default(self, obj):
        match obj:
            case np.integer():
                return int(obj)
            case np.floating():
                return float(obj)
            case np.ndarray():
                return obj.tolist()
            case dict():
                return obj.__dict__
            case str():
                return str(obj)
            case datetime.datetime():
                return datetime.datetime.strftime(obj, "%m-%d-%Y_%H-%M-%S")
            case _:
                return super(CustomEncoder, self).default(obj)

################################# Logger functions ####################################
#FUNCTION Logging Futures
def get_file_handler(log_dir:Path)->logging.FileHandler:
    """Assigns the saved file logger format and location to be saved

    Args:
        log_dir (Path): Path to where you want the log saved

    Returns:
        filehandler(handler): This will handle the logger's format and file management
    """	
    log_format = "%(asctime)s|%(levelname)-8s|%(lineno)-4d|%(funcName)-13s|%(message)-108s|" 
                 #f"%(asctime)s - [%(levelname)s] - (%(funcName)s(%(lineno)d)) - %(message)s"
    # current_date = time.strftime("%m_%d_%Y")
    file_handler = logging.FileHandler(log_dir)
    file_handler.setFormatter(logging.Formatter(log_format, "%m-%d-%Y %H:%M:%S"))
    return file_handler

def get_rich_handler(console:Console)-> RichHandler:
    """Assigns the rich format that prints out to your terminal

    Args:
        console (Console): Reference to your terminal

    Returns:
        rh(RichHandler): This will format your terminal output
    """
    rich_format = "|%(funcName)-13s| %(message)s"
    rh = RichHandler(console=console)
    rh.setFormatter(logging.Formatter(rich_format))
    return rh

def get_logger(console:Console, log_dir:Path)->logging.Logger:
    """Loads logger instance.  When given a path and access to the terminal output.  The logger will save a log of all records, as well as print it out to your terminal. Propogate set to False assigns all captured log messages to both handlers.

    Args:
        log_dir (Path): Path you want the logs saved
        console (Console): Reference to your terminal

    Returns:
        logger: Returns custom logger object.  Info level reporting with a file handler and rich handler to properly terminal print
    """

    #Load logger and set basic level
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    #Load file handler for how to format the log file.
    file_handler = get_file_handler(log_dir)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    #Don't need to load rich handler in this instance because the TUI will handle all messaging
    rich_handler = get_rich_handler(console)
    rich_handler.setLevel(logging.INFO)
    logger.addHandler(rich_handler)
    logger.propagate = False
    return logger


#FUNCTION get time
def get_time():
    """Function for getting current time

    Returns:
        t_adjusted (str): String of current time
    """
    current_t_s = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    return current_t_s

# def move_log():
#     ts = datetime.datetime.strptime(start_time, "%m-%d-%Y_%H-%M-%S")
#     year = ts.year
#     month = ts.month
#     destination_path = PurePath(
#         Path("./data/logs"),
#         Path(f"{year}"),
#         Path(f"{month}")
#     )
#     if not exists(destination_path):
#         os.makedirs(destination_path)
#     shutil.move(log_dir, destination_path)


################################# Global Vars ####################################
start_time = get_time()
console = Console(color_system="auto", stderr=True)
log_dir = PurePath(Path.cwd(), Path(f'./data/logs/{start_time.split("_")[0]}.log'))
logger = get_logger(log_dir=log_dir, console=console)

#FUNCTION Log time
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
            logger.warning(f"{fn.__name__} ran in {took:.2f}s")
        elif took <= 3600:
            logger.warning(f"{fn.__name__} ran in {(took)/60:.2f}m")		
        else:
            logger.warning(f"{fn.__name__} ran in {(took)/3600:.2f}h")
        return out
    return inner

################################# Date/Load/Save Funcs ####################################
#FUNCTION Save Data
def save_data(timepoint:dataclass, cdate:str, jsondata:dict):
    """This function saves the CPU/GPU data to the daily JSON file. It adds the key as the current time point the script was run.  Then deletes the id key from the updated dictionary. No need to store it twice.

    Args:
        timepoint (dataclass): Custom Data Container
        cdate (str) : Current Date
        jsondata (dict): Dictionary of historical data
    """
    id = timepoint.id
    jsondata[id] = timepoint.__dict__
    jsondata[id].pop("id")
    out_json = json.dumps(jsondata, indent=2, cls=CustomEncoder)
    with open(f"./data/json/{cdate}.json", "w") as out_f:
        out_f.write(out_json)

#FUNCTION Load Historical
def load_historical(fp:str)->dict:
    """Loads saved JSON data

    Args:
        fp    (str): File path for saving
    Returns:
        jsondata (JSON): dictionary version of saved JSON
    """
    
    if exists(fp):
        with open(fp, "r") as f:
            jsondata = json.loads(f.read())
            return jsondata	

#FUNCTION Convert Date
def date_convert(str_time:str)->datetime:
    """When Loading the historical data.  Turn all the published dates into datetime objects so they can be sorted in the save routine. 

    Args:
        str_time (str): Converts a string to a datetime object 

    Returns:
        dateOb (datetime): str_time as a datetime object
    """    
    dateOb = datetime.datetime.strptime(str_time,'%m-%d-%Y-%H-%M-%S')
    dateOb = np.datetime64(dateOb)
    return dateOb

def convert_dtypes(data: dict = None):
    """Recursively convert string values in a nested dictionary to integers or floats.

    Args:
        data (dict): Input dictionary with string values.

    Returns:
        dict: Dictionary with converted data types.
    """
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, dict):
                data[key] = convert_dtypes(val)
            elif isinstance(val, str):
                data[key] = _convert_str_to_number(val)
        return data

def _convert_str_to_number(val: str):
    """Helper function to convert string to int, then float.  If neither work, it returns it as a string.

    Args:
        val (str): Value to be converted

    Returns:
        val (type): Returns converted type if no error is introduced in the conversion.
    """
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return str(val)