import os
import subprocess
import time
import re
import json
from subprocess import check_output

# 1. Set-Up Environment Variables for IC Installation

def set_config():
    global k2home, k2cloud, customer_id, token, k2_group_name, k2_group_env, installer_path, validator, microagent 
    try:
        file = open("config.json", "r")
        config = json.loads(file.read())
        k2cloud= config["k2cloud"]
        customer_id=config["customer_id"]
        token=config["token"]
        k2home = config["k2home"]
        k2_group_name = config["k2GroupName"]
        k2_group_env = config["k2GroupEnv"]
        validator = config["validator"]
        microagent = config["microagent"]
        file.close()
    except:
        print("\033[1;31m\nError occurred in config.json file !\033[0m\n")
        quit() 

# 2. CHECKING IF K2 AGENT IS ALREADY INSTALLED  

def is_k2_installed():
    print("# Checking if K2 Agent is already installed ! #")
    flag1=0
    flag2=0
    flag3=0
    containers = check_output(["docker", "ps", "-a"]).decode("utf-8").split("\n")
    for name in containers:
        if name.find("k2-db") != -1:
            flag1=1
        if name.find("k2-validator") != -1:
            flag2=1
        if name.find("k2-micro-agent") != -1:
            flag3=1
    if flag1 or flag2 or flag3:
        print("\033[1;31m\nPLEASE REMOVE ALREADY INSTALLED K2 COMPONENTS !\033[0m\n")
        quit()

# DOWNLOADING INSTALLER FROM K2M ACCOUNT

def get_installer():
    global installer_path
    print("\nDOWNLOADING V2 INSTALLER FROM K2M CLOUD ACCOUNT ...\n")
    installer_cmd = "wget -O vm-all.zip '"+k2cloud+"/centralmanager/api/v2/help/installers/2.0.0-rc11/download/"+customer_id+"/"+token+"/vm-all?isDocker=true&groupName="+k2_group_name+"&agentDeploymentEnvironment="+k2_group_env+"&pullPolicyRequired=true'"
    print(installer_cmd) 
    try:
        subprocess.run(["rm", "-rf", "k2install", "vm-all.zip"]) 
        installer_log = check_output(installer_cmd, shell=True).decode("utf-8").split("\n")
        for log in installer_log:
            if log.find("‘vm-all.zip’ saved") == -1:
                download = 1
        if not download:
            quit()
        subprocess.run(["unzip", "vm-all.zip"])  
        installer_path = os.getcwd() + "/k2install" 
        print("\nINSTALLER EXTRACTED SUCCESSFULLY\n")
    except:
        print("\033[1;31m\nError occured in Downloading Installer from k2m cloud !\033[0m\n")
        quit()

# 3. Updating Validator and Microagent version in .agent.properties file

def update_agent_properties():
    print("UPDATING AGENT PROPERTIES FILE\n")
    try:
        f = open(installer_path+"/.agent.properties", "r")
        agent_data = f.readlines()
        f.close()
        count=0
        for line in agent_data:
            if line.find("prevent_web_agent_image_tag") != -1:
                agent_data[count] = "prevent_web_agent_image_tag=validator-"+validator+"\n"
                print(agent_data[count])
            elif line.find("micro_agent_image_tag") != -1:
                agent_data[count] = "micro_agent_image_tag=microagent-"+microagent+"\n"
                print(agent_data[count])
            elif line.find("prevent_web_agent_image") != -1:
                agent_data[count] = "prevent_web_agent_image=k2cyber/k2-intcode-agent\n"
            elif line.find("micro_agent_image") != -1:
                agent_data[count] = "micro_agent_image=k2cyber/k2-intcode-agent\n"
            count+=1
        f = open(installer_path+"/.agent.properties", "w")
        f.writelines(agent_data)
        f.close()
    except:
        print("\033[1;31m\nException occured in updating agent file !\033[0m\n")
        quit()

# 4. INSTALLATION of IC COMPONENTS

def install_k2_agent():
    print("\033[1;32m\nINSTALLING K2 COMPONENTS !\033[0m\n")
    os.chdir(installer_path)
    try:
        install_log = check_output(["bash", "k2install.sh", "-i", "prevent-web"]).decode("utf-8").split("\n")
        is_installed=0
        for line in install_log:
            if "Congratulations, You've Successfully Installed K2 DB, K2 Validator and K2 Micro Agent !" in line:
                print("\033[1;32m\nK2 AGENT INSTALLATION COMPLETED !\033[0m\n")
                is_installed=1
        if is_installed==0:
                print("\033[1;31m\nK2 AGENT COULD NOT INSTALLED !\033[0m\n")
                quit()
    except:
        print("\033[1;31m\nError in Installing K2 Agent! Please check config\033[0m\n")
        quit()

# 5. Getting Int-Code ID 

def get_ic_id():
    list1 = check_output(["ls", "-lrth", k2home + "k2root/logs/int-code/"])
    list1 = list1.decode("utf-8").split()
    ic_id = list1[-1]
    return ic_id

# 6. GETTING APPLICATION CONFIGURATIONS AND KNOWN DETAILS

def set_input_config(work_dir):
    # app config details
    global app_name, app_run_command, port, start_time, start_url, crawl_command, result_time, vulnerable_apis, vulnerable_urls, vulnerability_data
    os.chdir(work_dir)
    try:
        file = open("input.json", "r")
        app_config = json.loads(file.read())
        app_name = app_config["app_name"]
        app_run_command = app_config["app_run_command"]
        port = app_config["port"]
        start_time = app_config["start_time"]
        start_url = app_config["start_url"]
        crawl_command = app_config["crawl_command"]
        result_time = app_config["result_time"] 
        # kwown vulnerabilities details
        vulnerable_apis=[]
        vulnerable_urls=[]
        vulnerability_data=[]
        for url in app_config["urls"]:
            vulnerable_urls.append(url[0]["uri"])
            index=0
            for apis in url:
                if index == 0:
                    uri=apis["uri"]
                elif index != 0:
                    pair=[apis["api_id"],0]
                    vulnerable_apis.append(pair)
                    ls=[uri,apis["api_id"],apis["vulnerability"],apis["vulnerable_key"]]
                    vulnerability_data.append(ls)
                index+=1
        file.close()
    except:
        print("\033[1;31m\nError occurred in input.json file !\033[0m\n")
        quit()  

# 7. Remove Docker Application Container
def remove_container(container_name):
    try:
        subprocess.run(["docker", "rm", "-f", container_name])
    except:
        print("Exception occured in removing app container !")
        quit()

#  Modification in App Run command according to configs
def modify_app_command(container_name):
    return app_run_command.format(policy=k2_group_name, k2home=k2home, container_name=container_name)

# 8. Run Docker Application Container 
def run_app(app_run_command,container_name):
    try:
        subprocess.run(app_run_command, shell=True)
        if port == "80":
            cmd="docker exec -it "+ container_name+ " bash " +k2home+"k2root/collectors/k2-php-agent/k2_php_agent_install_script.sh --allow-server-restart=TRUE"
            print(cmd)
            subprocess.run(cmd, shell=True) 
    except:
        print("\n\033[1;31mException occured: APPLICATION COULD NOT STARTED !! EXITING.\033[0m \n")
        quit()

# 9. CHECKING FOR THE APPLICATION START

def check_app_start(container_name):
    #curl = "docker exec -it "+ container_name +' curl -s -o /dev/null -w "%{http_code}" http://localhost:'+port+"/forkexec-demo/"
    curl="docker exec -it "+ container_name +' curl -s -o /dev/null -w "%{http_code}" '+ start_url
    if start_url == "":
        curl="docker exec -it "+ container_name +' curl -s -o /dev/null -w "%{http_code}" http://localhost:'+port 
    print(curl)
    print("Waiting for Application to start : ",start_time,"sec")
    time.sleep(start_time)
    for i in range(0,6):
        try:
            status, res = subprocess.getstatusoutput(curl)
            if res == "200":
                print("\033[1;32m\nAPPLICATION STARTED !\033[0m\n")
                break
            elif i == 5:
                quit()
            else:
                print("Taking much time than usual, waiting more...")
                time.sleep(5) 
        except:
                print("\n\033[1;31mException occured: APPLICATION COULD NOT STARTED !! EXITING.\033[0m \n")
                quit()

# 10. DETECTION OF AGENT ATTACHMENT and GETTING APPLICATION-UUID 

def get_app_uuid(container_name):
    appuid=""
    if port == "80" or port == "8084":
        try:
            cmd = "ls -lrth " + k2home+"k2root/logs/language-agent"	
            appuid = check_output(cmd, shell=True).decode("utf-8").split()[-1]	
            print("\033[1;32mLANGUAGE AGENT IS ATTACHED !\033[0m\n")
            return appuid
        except:
            print("\033[1;31m\nERROR: language-Agent Logs are not Generated! EXITING\033[0m \n")
            quit()
    try:
        app_log_command = "docker logs "+container_name
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
        if not appuid:
            print("\033[1;31m\nERROR : LANGUAGE AGENT IS NOT CONNECTED !!\033[0m")
            quit() 
    except:
        print("\033[1;31m\nError occured while fetching app log! EXITING\033[0m \n")
        quit()
    return appuid

# 11. VERIFICATION OF APP-INFO 

def check_app_info(appuid):
    lc_log_path =k2home + "k2root/logs/language-agent/"+ appuid	
    print(lc_log_path)	
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')	
    lc_log_path = ansi_escape.sub('', lc_log_path)
    os.chdir(lc_log_path)
    lc_logs = check_output(["ls"]).decode("utf-8").split()
    for lc in lc_logs:
        if lc.find("init") == -1 and lc.find("agent") != -1:
            lc_log = lc 
    app_info = 0
    for t in range(0,6):
        file1 = open(lc_log, "r")
        for line in file1:  
            if 'applicationinfo' in line:	
                print("\033[1;32m\nAPP INFO GENERATED !\033[0m\n") 
                app_info=1
                break 
        file1.close() 
        if app_info == 1:
            break
        else:
            print("Waiting for app info generation...") 
            time.sleep(5)
    if app_info == 0: 
        print("\033[1;31m\nERROR : APP INFO WAS NOT GENERATED !! EXITING\033[0m \n")
        quit()

# 12. URLs to be Scanned Finding

def find_scan_uri(container_name):
    uris = set() 
    print("\n\033[1mURIs TO BE SCANNED:\033[0m\n")
    try: 
        script = crawl_command.split()[1]
        file = check_output(["docker", "exec", "-it", container_name, "cat", script]).decode("utf-8").split("\n")
        for line in file:      
            if "curl" in line and "localhost:"+port in line:
                    for word in line.split():
                        if "localhost" in word:
                            uris.add(word.split("?")[0].split("localhost:"+port)[-1].split(")")[0].split("'")[0].split('"')[0])
    except:
        print("\033[1;31mERROR : No Attack.sh script Found !\033[0m \n")
    for uri in uris:
        if uri != "-sw" and uri != "request":
            print(uri)

# 13. STARTING DYNAMIC SCANNING 

def start_ds(container_name):
    print("\033[1;32m\nSTARTING DYNAMIC SCANNING ...\033[0m\n")
    # executing attack.sh script
    docker_crawl_command = "docker exec -d "+ container_name + " " + crawl_command
    print(docker_crawl_command)
    try:
        subprocess.run(docker_crawl_command, shell=True)
    except:
        print("\033[1;31m\nERROR : CRAWLING IS NOT DONE ON THE APPLICATION !! EXITING\033[0m \n")
        quit() 

# 14. GETTING RESULT 

def get_result(ic_log_path, appuid):
    global detected_apis, result
    os.chdir(ic_log_path)
    print("\nWaiting for ", round(result_time/60), "minutes.")
    time.sleep(result_time)
    print("\033[1;32m\nRESULT:\033[0;37m\n=======")
    index=0
    result=[]
    detected_apis=[]
    json_result_data=[]
    with open('k2-vulnerability-record.log','r') as file: 
        for line in file: 
            for word in line.split("\n"):
                index=0
                if not word:
                    continue 
                for j in word:
                    if j == "{":
                        break
                    index+=1
                if index > 100:
                   json_result_data.append(json.loads(word[index: : ]))
        file.close()
    for record in json_result_data:
        if record["applicationUUID"] == appuid:
            index=0
            for values in record["vulnerabilityDetail"]:
                data=[]
                data.append(record["httpRequestMapping"]["baseRequest"]["requestURI"])
                data.append(record["apiId"]) 
                data.append(record["vulnerabilityDetail"][index]["type"])
                key_map=record["vulnerabilityDetail"][index]["target"]
                data.append(record["httpRequestMapping"]["userValueMap"][key_map]["key"])
                index+=1
                if data not in result:
                    result.append(data)
                    pair=[record["apiId"],0]
                    detected_apis.append(pair)
# 15. DETECT MATCHED APIs

def match_api():
    global vulnerable_apis, detected_apis 
    index1=0
    for api1 in vulnerability_data:
        index2=0
        for api2 in result:
            if api1[0] == api2[0] and api1[1] == api2[1] and api1[2] == api2[2] and api1[3] == api2[3]:
                vulnerable_apis[index1][1]=1
                detected_apis[index2][1]=1
            index2+=1 
        index1+=1

# 16. PRINT VULNERABILITIES DATA (matched and unmatched)

def show_vulnerability(key):
    index=0
    count=0
    print("{:<15} {:<40} {:<40} {:<40}".format('S.NO','URI','VULNERABILITY','VULNERABLE KEY'))
    print("{:<15} {:<40} {:<40} {:<40}".format('----','---','-------------','--------------'))
    for data in vulnerability_data:
        if vulnerable_apis[index][1] == key:
            count+=1
            print("{:<15} {:<40} {:<40} {:<40}".format(count,data[0],data[2],data[3]),"\n")
        index+=1
    return count

# 17. PRINT EXTRA DETECTED VULNERABILITIES 

def show_unexpected_vulnerablity():	
    index=0	
    count=0	
    print("{:<15} {:<40} {:<40} {:<40}".format('S.NO','URI','VULNERABILITY','ATTACK KEY'))	
    print("{:<15} {:<40} {:<40} {:<40}".format('----','---','-------------','----------'))	
    for data in result:	
        if detected_apis[index][1] == 0:	
            print("{:<15} {:<40} {:<40} {:<40}".format(count+1,data[0],data[2],data[3]),"\n")
            count+=1
        index+=1
    return count

# 18. CONCLUDING RESULT

def conclusion(count1, count2, count3):
    print("\033[1;32m\nFINAL CONCLUSION RESULT: \033[0m\n=======================\n")
    print("{:<35} {:<35} {:<30} {:<30} {:<30} {:<35}".format('App Name','Total Expected Vulnerabilities','Found Vulnerabilities','Not Found Vulnerabilities','Unexpected Vulnerabilities', 'SUCCESS RESULT'))	
    print("{:<35} {:<35} {:<30} {:<30} {:<30} {:<35}".format('--------','------------------------------','---------------------','-------------------------','--------------------------', '--------------'))
    print("{:<35}   {:<35} {:<30} {:<30} {:<30} {:<0}".format(app_name, len(vulnerable_apis),count1, count2,count3,round((count1*100)/len(vulnerable_apis))),"%\n")
