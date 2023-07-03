from dotenv import dotenv_values

config = dotenv_values(".env")

def get_shodan_key():
    SHODAN_API_KEY = config["SHODAN_API_KEY"]
    return SHODAN_API_KEY

def get_working_dir():
    WORKINGDIR = config["WORKINGDIR"]
    return WORKINGDIR