import os
def init_config(in_sConfigFileName) :
    from configparser import ConfigParser
    # instantiate
    if not os.path.exists(in_sConfigFileName):
        raise Exception('init_config:: file ' + in_sConfigFileName + ' does not exist ')
    config = ConfigParser()
    # parse existing file
    config.read(in_sConfigFileName)
    return config
def build_working_hysteresis_path(config) :
    sRunName = config.get('Run', 'sRunNameHysteresis')
    sBasePath = config.get('FilePth', 'sBasePath')
    sBasePath = sBasePath.replace("\\\\", "\\")
    threshold = config.get("FixedHysteresisInput","threshold")

    sBasePath = os.path.join(sBasePath, sRunName)
    sBasePathFreq = os.path.join(sBasePath, config.get('Inputs', 'Frequency'))
    sFixedHysteresisPath =  config.get('FilePth', 'sFixedHysteresisPath')
    sPath = os.path.join(sBasePathFreq,sFixedHysteresisPath)

    if not os.path.exists(sPath):
        os.makedirs(sPath)
    return sPath
