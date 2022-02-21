from logging import getLogger,INFO, StreamHandler,FileHandler,Formatter, DEBUG,WARNING,ERROR,CRITICAL
import os

logger = None;

def print_info(msg,mode="INFO"):
    if (logger == None):
        print(msg);
    else:
        if (mode == "INFO"):
            logger.info(msg);
        else:
            raise Exception("not implemented yet");

def get_logger():
    return logger;

def create_logger(LEVEL,output_folderPath,mode="both"):
    
    mode_candidate = ["both","file","stdout"]
    
    os.makedirs(output_folderPath,exist_ok=True);

    Level = getLevel(LEVEL);
    formatter = Formatter('[%(asctime)s] [%(levelname)s] :  %(message)s')
    global logger;
    logger = getLogger(__name__);

    ## normal handler
    handler = StreamHandler();
    handler.setLevel(Level);
    handler.setFormatter(formatter);

    output_folderPath = output_folderPath[:-1] if output_folderPath.endswith("/") else output_folderPath;

    handler_file = FileHandler(filename=output_folderPath+"/logger.log");
    handler_file.setLevel(Level)
    handler_file.setFormatter(formatter)

    logger.setLevel(Level);
    logger.addHandler(handler);
    logger.addHandler(handler_file);

def getLevel(Level_str):
    if(Level_str.upper() == "DEBUG"):
        return DEBUG;
    elif(Level_str.upper() == "INFO"):
        return INFO;
    elif (Level_str.upper() == "WARNING"):
        return WARNING;
    elif (Level_str.upper() == "ERROR"):
        return ERROR;
    elif (Level_str.upper() == "CRITICAL"):
        return CRITICAL;
    else:
        raise Exception("There is no such hubmap-kidney-segmentation level: " + Level_str.upper());