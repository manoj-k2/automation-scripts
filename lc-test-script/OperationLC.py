import os
import time
import json
import rich
import re
import subprocess
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.web import JsonLexer
from pprint import pprint
from subprocess import check_output

# k2home="/opt/k2root"
# appuid="23335_2bffac66-17ed-411a-957b-029209bed14b"

def set_config():
    global k2home,appuid,container_id,port,first
    try:
        file = open("config.json", "r")
        config = json.loads(file.read()) 
        k2home = config["k2home"]
        appuid = config["appuid"]
        container_id = config["containerId"]
        port = config["port"]
        first= config["first_data"] 
        file.close()
        print("Getting data for container:",container_id,"\n")
    except:
        print("\033[1;31m\nError occurred in config.json file !\033[0m\n")
        #quit()  

def pretty_json_print(string,json_name):
    color=1
    pretty_json=json.dumps(string, indent = 5)   
    header_str="\n======================\n"+json_name+":\n======================\n"
    if color == 1:
        colorful_json = highlight(pretty_json,lexer=JsonLexer(),formatter=Terminal256Formatter(),)
        print(header_str+"\n"+colorful_json)
    else:     
        rich.print_json(pretty_json) 

def fetch_json(line):
    #print(line,"\nn\n")
    for word in line.split("\n"):
        index=0
        if not word:
            continue 
        for j in word:
            if j == "{":
                break
            index+=1
        return json.loads(word[index: : ])

def get_lc_file():
    global lc_log
    lc_log_path =k2home + "k2root/logs/language-agent/"+ appuid	
    #print(lc_log_path)	
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')	
    lc_log_path = ansi_escape.sub('', lc_log_path)
    os.chdir(lc_log_path)
    lc_logs = check_output(["ls"]).decode("utf-8").split()
    for lc in lc_logs:
        if lc.find("init") == -1 and lc.find("agent") != -1:
            lc_log = lc 

def get_ic_file():
    global ic_dir
    cmd = "ls -lrth " + k2home+"k2root/logs/int-code/"	
    ic_id = check_output(cmd, shell=True).decode("utf-8").split()[-1]
    ic_dir= k2home+"k2root/logs/int-code/"+ic_id+"/"

def get_json_info(json_name):
    print("\033[1;33mgetting "+json_name+" data...\033[0m")
    json_info = 0
    #print(lc_log)
    for t in range(0,60):    # waiting time = 10 min
        json_result_data=[]      
        file1 = open(lc_log, "r")
        for line in file1:  
            if json_name in line:	
                #print(line)
                json_data=fetch_json(line)
                json_result_data.append(json_data)
                json_info=1
                if first == True:
                    break 
        file1.close() 
        if json_info == 1:
            #print("f")
            break
        else:
            #print("Waiting for "+json_name+" json info ...") 
            time.sleep(10)  
    if json_result_data :  
        print(json_name,"found:",len(json_result_data))
        pretty_json_print(json_result_data[0],json_name)
    else:
        print("\033[1;31m"+json_name+" not found !\033[0m")

def get_errors():
    print("\nERROR:\n=======\n")
    for t in range(0,10):    # waiting time = 10 min
        error_data=[]    
        json_info=0  
        file1 = open(lc_log, "r")
        for line in file1:  
            if json_info ==1:
                #json_result_data.append(line)
                json_info=0
            if "Error response :" in line:	 
                json_info=1
                error_data.append(line)
        file1.close() 
        for error in error_data:
            print(error)
        break

def get_app_uuid():
    global appuid
    try:
        curl="curl localhost:"+port
        log = check_output(curl,stderr=subprocess.STDOUT, shell=True)
    except:
        print("Please start the application")
    if port == "80" or port == "8084":
        try:
            cmd = "ls -lrth " + k2home+"k2root/logs/language-agent"	
            appuid = check_output(cmd, shell=True).decode("utf-8").split()[-1]	
            print("\033[1;32mLANGUAGE AGENT IS ATTACHED !\033[0m\n")
            return
        except:
            print("\033[1;31m\nERROR: language-Agent Logs are not Generated!\033[0m \n")
            #quit()
    try:
        app_log_command = "docker logs "+container_id
        for t in range(0,6):
            app_log = check_output(app_log_command, shell=True)
            app_log = app_log.decode("utf-8").split('\n')
            for line in app_log:
                if line.find("K2 Ruby collector attached to process") != -1:        # RUBY CASE
                    words = line.split()
                    appuid = words[words.index("applicationUUID") + 2]
                    break
                elif line.find("This application instance is now being protected by K2 Agent ") != -1:   # JAVA CASE
                    words = line.split()
                    appuid = words[words.index("id") + 1]
                    break   
                elif line.find("applicationUUID:") != -1:         #  PYTHON &  NODE CASE 
                    words = line.split()
                    appuid = words[words.index("applicationUUID:") + 1].split(".")[0]
                    break
            if appuid:
                print("\033[1;32mLANGUAGE AGENT IS ATTACHED !\033[0m\n") 
                break
            else:
                print("Waiting for Agent attachment and Application uuid...")
                time.sleep(5)    
        print("ApplicationUUID: "+appuid) 
    except:
        print("\033[1;31m\nError occured in appUUID while fetching app log!\033[0m")
        print("Using given appUUID: ",appuid)
        #quit()

def get_ic_json(json_name):
    print("\033[1;33m\ngetting CVE scan result data...\033[0m")
    ic_log=ic_dir+"prevent_web.log"
    #print(lc_log)
    json_result_data=[]      
    file1 = open(ic_log, "r")
    for line in file1:  
        if json_name in line and appuid in line:	
            json_data=fetch_json(line)
            json_result_data.append(json_data)
    file1.close() 
    if json_result_data:
        print(json_name,"found:",len(json_result_data))
        ask=input("\033[96mDo you want to show cve scan result (y/n): \033[0m")
        if ask == "yes" or ask =="y": 
            for js in json_result_data:
                pretty_json_print(js,json_name+" "+js["applicationName"])
    else:
        print("\033[1;31m"+json_name+" not found !\033[0m") 

def remove_extra_data(line):
    flag=0
    for index in range( len(line) - 2, -1, -1) :
        if line[index] == "}" :
            return json.loads(line[:index+1 :])

def get_attacks():
    json_result_data=[]
    file1 = open(ic_dir+"prevent_web.log", "r")
    for line in file1:  
        if "Validated event :" in line and appuid in line and "Attack" in line :	 # 
            for word in line.split("\n"):
                index=0
                if not word:
                    continue 
                for j in word:
                    if j == "{":
                        break
                    index+=1
                json_data=remove_extra_data(word[index: : ])
                json_result_data.append(json_data)
    file1.close()  
    return json_result_data

def validate_attack():
    print("\033[1;33m\ngetting Validated attacks data...\033[0m")
    wait_time=10
    old_attack_count=0
    old_attacks= get_attacks()
    old_attack_count=len(old_attacks)
    last_timestamp = old_attacks[-1]["eventGenerationTime"]
    print("Old attacks counts: ", old_attack_count)
    attack_curl="docker exec -it "+container_id+" bash /attack.sh all"
    # attacking 
    check_output(attack_curl,stderr=subprocess.STDOUT, shell=True)
    print("waiting for attacks:",wait_time,"second")
    time.sleep(wait_time)
    json_result_data = get_attacks()
    if json_result_data :  
        print("New attacks counts:",len(json_result_data)-old_attack_count)
        print("\nFOUND THESE VULNERABILITIES : \n===========================")
        count=1
        for js in json_result_data:
            if count > old_attack_count: 
                print(js["vulnerabilityCaseType"])
            count+=1 
        ask=input("\033[96m\nDo you want to show all attacks (y/n): \033[0m")
        if ask == "yes" or ask =="y":
            count=1
            for js in json_result_data:
                if count > old_attack_count:
                    pretty_json_print(js,"Attack: "+ js["vulnerabilityCaseType"])   
                count+=1 
    else:
        print("\033[1;31m attacks are not found !\033[0m")
        