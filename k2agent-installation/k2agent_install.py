import os
import sys
import paramiko 
import json

def set_config():
    global k2home, k2cloud, customer_id, token, k2_group_name, k2_group_env, installer_path, validator, microagent,rc,vm,user,public_ip,install_dir,cd_install_dir,root,pem_file,isDocker
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
        rc = config["rc"]
        vm = config["vm"]
        public_ip = config["public_ip"]
        user = config["user"]
        pem_file=config["pem_file"] 
        install_dir = config["install_dir"]  
        if(config["root"] == True):
            root="sudo "
        else: 
            root=""
        if(config["docker"] == True):
            isDocker=1
        else: 
            isDocker=0
        cd_install_dir="cd "+install_dir+"; "
        file.close()
    except:
        print("\033[1;31m\nError occurred in config.json file !\033[0m\n")
        quit() 

def vm_ic_install():
    print()

def aws_ic_install():
    def get_installer():
        global installer_path
        stdin, stdout, stderr = con.exec_command("mkdir -p "+install_dir)
        print("\033[1;33m\nDownloading v2 installer from k2m cloud account...\033[0m")
        if isDocker==1:
            print("Docker installer\n")
            installer_cmd = cd_install_dir+"wget -O vm-all.zip '"+k2cloud+"/centralmanager/api/v2/help/installers/"+rc+"/download/"+customer_id+"/"+token+"/vm-all?isDocker=true&groupName="+k2_group_name+"&agentDeploymentEnvironment="+k2_group_env+"&pullPolicyRequired=true'"
        else:
            print("Non-Docker installer\n")
            installer_cmd = cd_install_dir+"wget -O vm-all.zip '"+k2cloud+"/centralmanager/api/v2/help/installers/"+rc+"/download/"+customer_id+"/"+token+"/vm-all?arch=linux_x64&isDocker=false&groupName="+k2_group_name+"&agentDeploymentEnvironment="+k2_group_env+"&pullPolicyRequired=true'" 
        #print(installer_cmd) 
        try:
            stdin, stdout, stderr = con.exec_command(installer_cmd,get_pty=True)
            for line in iter(stdout.readline, ""):
                print(line, end="")
            stdin, stdout, stderr =con.exec_command(cd_install_dir+"unzip -o vm-all.zip")
            print(stderr.read().decode("utf8"))
            #print("\nINSTALLER EXTRACTED SUCCESSFULLY\n")
            installer_path=install_dir+"k2install/"
        except:
            print("\033[1;31m\nError occured in Downloading Installer from k2m cloud !\033[0m\n")
            quit()
        print()

    def update_agent_file():
        print("\033[1;33mUpdating .agent.properties files...\n\033[0m")
        try:
            stdin, stdout, stderr =con.exec_command("sed -i '/prevent_web_agent_image=/c prevent_web_agent_image=k2cyber/k2-intcode-agent' "+installer_path+".agent.properties")
            print(stderr.read().decode("utf8")) 
            stdin, stdout, stderr =con.exec_command("sed -i '/micro_agent_image=/c micro_agent_image=k2cyber/k2-intcode-agent' "+installer_path+".agent.properties")
            stdin, stdout, stderr =con.exec_command('sed -i "/prevent_web_agent_image_tag/c prevent_web_agent_image_tag=validator-"'+validator+" "+installer_path+".agent.properties")
            stdin, stdout, stderr =con.exec_command("sed -i '/micro_agent_image_tag/c micro_agent_image_tag=microagent-"+microagent+"' "+installer_path+".agent.properties")
        except:
            print("\033[1;31m\nException occured in updating agent file !\033[0m\n")
            quit()

    def install_k2():
        print("\033[1;33mInstalling k2 components...\033[0m",end="")
        if root == "sudo ":
            print(" as root user")
        else:
            print(" as non-root user")
        #stdin, stdout, stderr = con.exec_command("docker ps",get_pty=True)
        stdin, stdout, stderr = con.exec_command("cd "+installer_path+"; "+root+"bash k2install.sh -i prevent-web",get_pty=True)
        for line in iter(stdout.readline, ""):
            print(line, end="") 
    try:
        con = paramiko.SSHClient()   
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        k = paramiko.RSAKey.from_private_key_file(pem_file)
        con = paramiko.SSHClient()
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        con.connect(public_ip, username=user, pkey=k, allow_agent=False, look_for_keys=False,timeout=10)   
        print("connected to aws instance: "+user+" "+public_ip)
        
        # Methods 
        get_installer()
        update_agent_file()
        install_k2()
        con.close()
        #except:
        #    print("trying with private ip address")
            #con.connect(private_ip, username=user, pkey=k, allow_agent=False, look_for_keys=False,timeout=10)
    except:
        exit()

set_config()
if len(sys.argv) > 1:
    if(sys.argv[1]=="aws"):
        aws_ic_install()
    else:
        vm_ic_install()
else:
    vm_ic_install()


# sample run commands:
# python3 k2agent_installation.py aws       # for aws instance 
# python3 k2agent_installation.py           # for vm 
