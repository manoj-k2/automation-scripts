import os
import subprocess
import time
import re
import json
import tty
import paramiko 
from scp import SCPClient
from subprocess import check_output

work_dir = os.getcwd()
rows, console_size = os.popen('stty size').read().split()  # Terminal size 

# Set-Up Environment Variables for IC Installation
def set_config():
    global k2cloud,customer_id,token,k2_group_name,k2_group_env,installer_path, validator,microagent,rc,validator_endpoint
    global without_machine,yandex_machine,machine_password,instana_run_cmd,without_app_run,with_app_run,port,yandex_time,curl
    try:
        file = open("config.json", "r")
        config = json.loads(file.read())
        k2cloud= config["k2cloud"]
        customer_id=config["customer_id"]
        token=config["token"]
        k2_group_name = config["k2GroupName"]
        k2_group_env = config["k2GroupEnv"]
        validator = config["validator"]
        microagent = config["microagent"]
        without_machine = config["without_machine"]
        yandex_machine = config["yandex_machine"]
        machine_password = config["machine_password"]
        without_app_run = config["without_app_run"]
        with_app_run = config["with_app_run"]
        rc=config["rc"]
        validator_endpoint=config["validator_endpoint"]
        yandex_time=config["yandex_time"] 
        temp = without_app_run.split(" ")
        port = temp[temp.index("-p")+1].split(":")[0]
        instana_run_cmd = "docker run --detach --name instana-agent --volume /var/run/docker.sock:/var/run/docker.sock --volume /dev:/dev --volume /sys:/sys --volume /var/log:/var/log --privileged --net=host --pid=host --ipc=host --env='INSTANA_AGENT_KEY=i6anpVVIQPyPvPqdcKxM8w' --env='INSTANA_AGENT_ENDPOINT=saas-us-west-2.instana.io' --env='INSTANA_AGENT_ENDPOINT_PORT=443' instana/agent" 
        installer_path = os.getcwd() + "/k2install" 
        if not config["start_url"] or config["start_url"] == "":
            curl = 'curl -s -o /dev/null -w "%{http_code}" http://localhost:'+port
        else:
            curl = 'curl -s -o /dev/null -w "%{http_code}" '+ config["start_url"]
        file.close()
    except:
        print("\033[1;31m\nError occurred in config.json file !\033[0m\n")
        quit() 

# Print Console size border line 
def console_border():
    for i in range(0, int(console_size)):
        print("-",end ="")
    print()

# Remove all containers on with machine 
def remove_all():
    try:
        print("\033[1;34mNOTE: REMOVING ALL THE CONTAINERS RUNNING ON WITH & WITHOUT MACHINES !\033[0m\n")
        cmd="docker rm -f $(docker ps -a -q)"
        subprocess.run(cmd, shell=True)
        subprocess.run(["rm","-rf","/opt/k2root/"])
    except:
        print("\033[1;31m\nError occurred in Removing all Container !\033[0m\n")
        quit()  

# CHECKING IF K2 AGENT IS ALREADY INSTALLED 

def run_instana():
    try:
        subprocess.run(instana_run_cmd, shell=True)
    except:
        print("\033[1;31m\nError occurred in running instana container !\033[0m\n")
        quit() 

# GET PRIVATE IP ADDRESS OF CURRENT MACHINE 

def get_my_ip():
    global my_ip
    try:
        cmd="hostname -I | awk '{print $1}'"
        my_ip = check_output(cmd, shell=True).decode("utf-8").split("\n")[0]
    except:
        print("Exception in getting private IP address of this machine.")  

# DOWNLOADING INSTALLER FROM K2M ACCOUNT

def get_installer():
    print("\nDOWNLOADING V2 INSTALLER FROM K2M CLOUD ACCOUNT ...\n")
    installer_cmd = "wget -O vm-all.zip '"+k2cloud+"/centralmanager/api/v2/help/installers/"+rc+"/download/"+customer_id+"/"+token+"/vm-all?isDocker=true&groupName="+k2_group_name+"&agentDeploymentEnvironment="+k2_group_env+"&pullPolicyRequired=true'"
    #print(installer_cmd) 
    try:
        subprocess.run(["rm", "-rf", "k2install", "vm-all.zip"], stdout=subprocess.DEVNULL,  stderr=subprocess.DEVNULL) 
        installer_log = check_output(installer_cmd, shell=True).decode("utf-8").split("\n")
        for log in installer_log:
            if log.find("‘vm-all.zip’ saved") == -1:
                download = 1
        if not download:
            quit()
        subprocess.run(["unzip", "vm-all.zip"], stdout=subprocess.DEVNULL,  stderr=subprocess.DEVNULL)  
        print("\nINSTALLER EXTRACTED SUCCESSFULLY\n")
    except:
        print("\033[1;31m\nError occured in Downloading Installer from k2m cloud !\033[0m\n")
        quit()

# Updating Validator and Microagent version in .agent.properties file

def update_k2_agent_file():
    if validator_endpoint:
        print("Updating env.properties file for Validator endpoints \n\033[1;36m")
        try:
            f = open(installer_path+"/env.properties", "r")
            agent_data = f.readlines()
            f.close()
            count=0
            for line in agent_data:
                if line.find("k2_agent_validator_endpoint") != -1:
                    agent_data[count] = "k2_agent_validator_endpoint=ws://"+validator_endpoint+":54321\n"
                    print(agent_data[count])
                elif line.find("k2_agent_resource_endpoint") != -1:
                    agent_data[count] = "k2_agent_resource_endpoint=http://"+validator_endpoint+":54322\n"
                    print(agent_data[count])
                count+=1
            f = open(installer_path+"/env.properties", "w")
            f.writelines(agent_data)
            f.close()
        except:
            print("\033[1;31m\nException occured in updating agent file !\033[0m\n")
            quit() 
    if k2cloud == "https://k2io.net":
        print("\033[0m")
        return
    print("\033[0mUpdating .agent.properties file for validator and microagent version\n\033[1;36m")
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
        print("\033[0m")
    except:
        print("\033[1;31m\nException occured in updating agent file !\033[0m\n")
        quit()

# INSTALLATION of IC COMPONENTS

# Install DB & Validator on Remote Machine 
def install_validator():
    def private_agent_install():
        script_path = "/root/kishan/v2-install-scripts"   # Install DB
        stdin, stdout, stderr = con.exec_command("bash "+script_path+"/install-db.sh")
        print("bash "+script_path+"/install-db.sh")
        #print(stderr.read().decode("utf8"))
        print(stdout.read().decode("utf8"))
        validator_cmd = "bash "+script_path+"/install-validator.sh private validator-"+validator+" IAST"  
        print(validator_cmd)
        stdin, stdout, stderr = con.exec_command(validator_cmd)
        #print(stderr.read().decode("utf8"))
        print(stdout.read().decode("utf8")) 
    
    def public_agent_install():
        print("Using Public Cloud account...")
        get_my_ip()
        con.exec_command("rm -rf /root/installer/k2install; mkdir -p /root/installer/")
        installer_cp_cmd="scp -r root@"+my_ip+":"+work_dir+"/k2install /root/installer/k2install"
        con.exec_command(installer_cp_cmd)
        time.sleep(5)
        install_ic_cmd="cd /root/installer/k2install/; bash k2install.sh -i prevent-web"
        stdin, stdout, stderr =con.exec_command(install_ic_cmd,get_pty=True) 
        for line in iter(stdout.readline, ""):
            print(line, end="")
        con.exec_command("docker rm -f k2-micro-agent")
        
    ### connection to validator machine
    con = paramiko.SSHClient()   
    con.load_system_host_keys("/root/.ssh/known_hosts") 
    con.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
    con.connect(validator_endpoint, password=machine_password)
    print("Connection Stablished to Machine: ",validator_endpoint,"\n")
    print("Checking if Validator is already installed on remote machine...")
    stdin, stdout, stderr = con.exec_command("docker ps")
    val="k2cyber/k2-agent-v2:validator-"+validator
    db = "arangodb/arangodb"
    db_check=0
    val_check=0 
    for line in stdout.read().decode("utf8").split("\n"):
        #print(line)
        if val in line :
            val_check = 1
        elif db in line:
            db_check = 1
    if val_check and db_check:
        print("IC is already installed on remote machine.")
        return 
    else:
        print("Validator-"+validator+" did not matched/ found on remote machine !")
        ask=input("\033[1;33m\nDo you want to install instana, db, validator on remote machine ?(y/n): \033[0m")
    if ask != "y" and ask != "yes":
        exit()
    print("\nInstalling: Instana, DB and Validator on remote machine...\n")  
    print("Removing Containers on remote-validator machine!")
    con.exec_command("docker rm -f $(docker ps -a -q)")
    time.sleep(5)
    con.exec_command(instana_run_cmd)
    if k2cloud != "https://k2io.net":
        private_agent_install()
    else:
        public_agent_install()

    # showing containers     
    stdin, stdout, stderr = con.exec_command("docker ps")
    print("\033[1;36mRunning Containers on Validator machine: "+ validator_endpoint,"\033[0m")
    console_border()
    print(stdout.read().decode("utf8"))
    console_border()

# Install IC on Local machine 
def install_k2_agent():
        print("\033[1;32m\nINSTALLING K2 COMPONENTS !\033[0m\n")
    #try:
        if not validator_endpoint:
            agent = "prevent-web"
        else:
            install_validator()
            agent = "micro-agent"
        os.chdir(installer_path)
        # updating k2 agent files 
        update_k2_agent_file()
        print("Installing: ",agent," on with machine...\n")
        install_log = check_output(["bash", "k2install.sh", "-i", agent]).decode("utf-8").split("\n")  # on local machine 
        string1="Congratulations, You've Successfully Installed K2 DB, K2 Validator and K2 Micro Agent !"
        string2="Congratulations, You've Successfully Installed K2 Micro Agent !"
        for line in install_log:
            if string1 in line or ( validator_endpoint and string2 in line ): 
                print("\033[1;32m\nK2 AGENT INSTALLATION COMPLETED !\033[0m\n")
                return 
        print("\033[1;31m\nK2 AGENT COULD NOT INSTALLED !\033[0m\n")
        quit()
    #except:
    #    print("\033[1;31m\nError in Installing K2 Agent! Please check config or Unistall previously installed k2 agent\033[0m\n")
    #    quit()

# Run Docker Application Container 

def run_app():
    global container_id, pull_app
    try:
        pull_app="docker pull "+ with_app_run.split(" ")[-1]
        subprocess.run(pull_app, shell=True) 
        container_id = check_output(with_app_run, shell=True).decode("utf-8").split()[-1]	
        print(with_app_run)
        print("App Container ID:",container_id)
        if port == "80":
            cmd="docker exec -it "+ container_id+" bash /opt/k2root/k2root/collectors/k2-php-agent/k2_php_agent_install_script.sh --allow-server-restart=TRUE"
            print(cmd)
            subprocess.run(cmd, shell=True) 
    except:
        print("\n\033[1;31mException occured: APPLICATION COULD NOT STARTED !! EXITING.\033[0m \n")
        quit()

# CHECKING FOR THE APPLICATION START

def check_app_start():
    print("Waiting for with-Application to start...")      # MAX TIME : 6 min
    for i in range(0,80):
        try:
            status, res = subprocess.getstatusoutput(curl)
            if res == "200":
                print("\033[32m\nApplication with IC started.\033[0m\n")
                return
            #print("Taking much time than usual, waiting more...")
            time.sleep(5) 
        except:
                print("\n\033[1;31mException occured: APPLICATION COULD NOT STARTED !! EXITING.\033[0m \n")
                quit()
    print("\n\033[1;31mError: With IC application could not started! Exiting\033[0m")
    quit()

# SHOW RUNNING CONTAINERS

def show_containers():
    try:
       get_my_ip()
       print("\033[1;36mRunning Containers on With-Machine:",my_ip,"\033[0m")
       cmd = "docker ps"
       running_containers = check_output(cmd, shell=True).decode("utf-8").split("\n")
       console_border()
       for cnt in running_containers:
           print(cnt)
       console_border()
    except:
       print("\n\033[1;31mError occured in showing running container on with machine.\033[0m \n")
       quit() 

# WITHOUT MACHINE OPERATIONS

def without_machine_connection():
    try:
        con = paramiko.SSHClient()   
        con.load_system_host_keys("/root/.ssh/known_hosts") 
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
        con.connect(without_machine, password=machine_password)
        print("\nConnection Stablished to Machine: ",without_machine,"\n")
        # REMOVE ALL CONTAINERS ON WITHOUT MACHINE
        remove_all_cmd = "docker rm -f $(docker ps -a -q)"
        con.exec_command(remove_all_cmd)
        # RUN INSTANA & APP CONTAINER
        time.sleep(5)      
        con.exec_command(instana_run_cmd)
        time.sleep(5)                    # wait for instana 
        con.exec_command(pull_app)
        print(pull_app) 
        stdin, stdout, stderr = con.exec_command(without_app_run)
        print(stdout.read().decode("utf8"))
        # checking app start 
        print(curl,"\nWaiting for without-Application to start...")     # MAX WAIT TIME : 6 min 
        for t in range(0,80):
            stdin, stdout, stderr = con.exec_command(curl)
            if stdout.read().decode("utf8") == "200":
                print("\033[32m\nApplication without IC started.\033[0m\n")
                break
            elif t == 79:
                print("\n\033[1;31mError: Without IC application could not started !\033[0m")
                quit()
            #print("Taking much time than usual, waiting more...")
            time.sleep(5) 

        stdin, stdout, stderr = con.exec_command("docker ps")
        print("\033[1;36mRunning Containers on Without machine: "+ without_machine,"\033[0m")
        console_border()
        print(stdout.read().decode("utf8"))
        console_border()
    except:
        print("\n\033[1;31mException occured: Could not perform operation on ssh without-machine !! EXITING.\033[0m \n")
        quit() 

# Getting with and Without yandex container run command

def get_yandex_commands():
    global with_yandex_cmd, without_yandex_cmd, language, with_path, without_path
    if port =="3000":
        language="ruby"
    elif port == "8080":
        language="java"
    elif port == "8084":
        language="go"
    elif port == "8000":
        language="python"
    elif port == "80":
        language= "php"
    else:
        language= "node"
    without_path="/root/longevity/"+language+"/without"
    with_path= "/root/longevity/"+language+"/with"
    with_yandex_cmd = "docker run -v $(pwd):/var/loadtest -v $SSH_AUTH_SOCK:/ssh-agent -e SSH_AUTH_SOCK=/ssh-agent --net host -itd --name yandex-"+language+"-with direvius/yandex-tank"
    without_yandex_cmd = "docker run -v $(pwd):/var/loadtest -v $SSH_AUTH_SOCK:/ssh-agent -e SSH_AUTH_SOCK=/ssh-agent --net host -itd --name yandex-"+language+"-without direvius/yandex-tank" 

# EDIT LOAD.YAML FILES

def edit_load_file(name,machine):
    try:
        f = open(name, "r")
        file_data = f.readlines()
        f.close()
        count=0
        for line in file_data:
            if line.find("address:") != -1:
                file_data[count] = "  address: "+machine+":"+port+"\n" 
            elif line.find("Host:") != -1:
                file_data[count] = "    - '[Host: "+machine+":"+port+"]'\n"  
            elif line.find("[Origin:") != -1:
                    #  - "[Origin: http://192.168.5.143:8084]"
                file_data[count] = '    - "[Origin: http://'+machine+':'+port+']"\n'   
            elif line.find("schedule:") != -1:
                file_data[count] = "    schedule: const(100, "+yandex_time+")\n"
                #print(agent_data[count])
            count+=1
        f = open(name, "w")
        f.writelines(file_data)
        f.close()
    except:
        print("\033[1;31m\nException occured in updating load.yaml file !\033[0m\n")
        quit()  

# YANDEX MACHINE OPERATIONS

def yandex_machine_connection():
    os.chdir(work_dir)
    con = paramiko.SSHClient()   
    #con.load_system_host_keys("/root/.ssh/known_hosts") 
    con.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
    con.connect(yandex_machine, password=machine_password)
    print("Connection Stablished to Machine: ",yandex_machine) 
    con.exec_command("mkdir /root/longevity_autorun/")
    print("Yandex Schedule: ", yandex_time)
    with SCPClient(con.get_transport()) as scp:
        scp.get(without_path+"/load.yaml", work_dir+"/without.yaml")
        scp.get(with_path+"/load.yaml", work_dir+"/with.yaml") 
    print("Editing load.yaml Files...")
    edit_load_file("without.yaml",without_machine)
    edit_load_file("with.yaml",my_ip)
    with SCPClient(con.get_transport()) as scp:
        scp.put(work_dir+"/without.yaml", without_path+"/load.yaml")
        scp.put(work_dir+"/with.yaml", with_path+"/load.yaml")
    without_yandex_command = without_yandex_cmd.replace("$(pwd)", without_path)
    with_yandex_command = with_yandex_cmd.replace("$(pwd)", with_path) 
    yandex_remove_cmd="docker rm -f yandex-"+language+"-without"+" yandex-"+language+"-with"
    #print(yandex_remove_cmd)
    stdin, stdout, stderr = con.exec_command(yandex_remove_cmd) 
    time.sleep(5)
    print(without_yandex_command,"\n",with_yandex_command)
    print("Running Yandex Containers...")
    stdin, stdout1, stderr1 = con.exec_command(without_yandex_command)
    stdin, stdout2, stderr2 = con.exec_command(with_yandex_command)
    print(stdout1.read().decode("utf8"),stdout2.read().decode("utf8"))
    time.sleep(10) 
    print("\n\033[1;32m+--------------------------------+")
    print("| YANDEX MACHINE SETUP COMPLETED |")
    print("+--------------------------------+\033[0m\n")
    stdin, stdout, stderr = con.exec_command("docker ps")
    print("\033[1;36mRunning Containers on Yandex machine: "+ yandex_machine,"\033[0m")
    console_border()
    print(stdout.read().decode("utf8"))
    console_border()
    
# Get Appuuid and language agent attachment

def get_app_uuid():
    print("Detecting Language Agent Attachement...\n")
    global appuid
    appuid=""
    if with_app_run.find("unicorn") != -1:
        cmd = "docker exec -it "+container_id +" cat /syscalls_ruby/log/unicorn.log"
        try:
            app_log=check_output(cmd, shell=True).decode("utf-8").split('\n')
            for line in app_log:
                if line.find("K2 Ruby collector attached to process") != -1:        
                    words = line.split()
                    appuid = words[words.index("applicationUUID") + 2]
                    return
        except:
            print("\033[1;31m\nERROR: Unicorn.log file not found! \033[0m \n")

    if port == "80" or port == "8084":
        try:
            cmd = "ls -lrth " + "/opt/k2root/k2root/logs/language-agent"	
            appuid = check_output(cmd, shell=True).decode("utf-8").split()[-1]	
            #print("\033[1;32mLANGUAGE AGENT IS ATTACHED !\033[0m\n")
            return
        except:
            print("\033[1;31m\nERROR: language-Agent Logs are not Generated! EXITING\033[0m \n")
            quit()
    try: 
        app_log_command = "docker logs "+container_id
        for t in range(0,10):
            app_log = check_output(app_log_command, shell=True)
            app_log = app_log.decode("utf-8").split('\n')
            for line in app_log:
                if line.find("K2 Ruby collector attached to process") != -1:        # RUBY CASE
                    words = line.split()
                    appuid = words[words.index("applicationUUID") + 2]
                    return
                elif line.find("This application instance is now being protected by K2 Agent ") != -1:   # JAVA CASE
                    words = line.split()
                    appuid = words[words.index("id") + 1]
                    return   
                elif line.find("applicationUUID:") != -1:         #  PYTHON &  NODE CASE 
                    words = line.split()
                    appuid = words[words.index("applicationUUID:") + 1].split(".")[0]
                    return
            print("Waiting for Agent attachment and Application uuid...")
            time.sleep(5)    
        if not appuid:
            print("\033[1;31m\nERROR : LANGUAGE AGENT IS NOT CONNECTED !!\033[0m")
            quit() 
    except:
        print("\033[1;31m\nError occured while fetching app log! EXITING\033[0m \n")
        quit()

# VERIFICATION OF APP-INFO 

def check_app_info():
    lc_log_path ="/opt/k2root/k2root/logs/language-agent/"+ appuid	
    print(lc_log_path)	
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')	
    lc_log_path = ansi_escape.sub('', lc_log_path)
    os.chdir(lc_log_path)
    lc_logs = check_output(["ls"]).decode("utf-8").split()
    for lc in lc_logs:
        if lc.find("init") == -1 and lc.find("agent") != -1:
            lc_log = lc 
    for t in range(0,6):
        file = open(lc_log, "r")
        for line in file:  
            if 'applicationinfo' in line:	
                print("\033[32m\nApplication info generated.\033[0m\n") 
                return 
        file.close() 
        print("Waiting for app info generation...") 
        time.sleep(5) 
    print("\033[1;31m\nERROR : APP INFO WAS NOT GENERATED !! EXITING\033[0m \n")
    quit()

