import os
import sys
import paramiko 


########     USER  INPUTS    #########
# For VM
vm="192.168.5.68"           

# For aws instance
public_ip="18.191.247.91"    # if dont work please provide private ip
user="ubuntu"             

k2home="/opt/k2root/"
log_dir=k2home+"k2root/logs/language-agent/"
home_dir = os.path.expanduser('~')
pem_file = home_dir+"/Downloads/k2-qa.pem"

####################################

def vm_lc_log():
    con = paramiko.SSHClient()   
    # con.load_system_host_keys("/root/.ssh/known_hosts") 
    con.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
    con.connect(vm, username="root", password="k2cyber")
    print("connected to vm: "+vm)
    stdin, stdout, stderr = con.exec_command("ls -t "+log_dir)
    appuuid=stdout.read().decode("utf8").split()[0]
    lc_path=log_dir+appuuid+"/"
    stdin, stdout, stderr = con.exec_command("ls "+lc_path) 
    for lc in stdout.read().decode("utf8").split():
        if lc.find("init") == -1 and lc.find("agent") != -1:
            lc_log_file = lc 
    tail_log_cmd="tail -F " + lc_path+lc_log_file
    print(tail_log_cmd)
    stdin, stdout, stderr = con.exec_command(tail_log_cmd,get_pty=True) 
    for line in iter(stdout.readline, ""):
        print(line, end="")
    con.close()


def aws_lc_log():
    #try:
        con = paramiko.SSHClient()   
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        k = paramiko.RSAKey.from_private_key_file(pem_file)
        con = paramiko.SSHClient()
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        con.connect(public_ip, username=user, pkey=k, allow_agent=False, look_for_keys=False,timeout=10)   
        print("connected to aws instance: "+public_ip)
        stdin, stdout, stderr = con.exec_command("ls -t "+log_dir)
        #print(log_dir)
        appuuid=stdout.read().decode("utf8").split()[0]
        #print(appuuid)
        lc_path=log_dir+appuuid+"/"
        stdin, stdout, stderr = con.exec_command("ls "+lc_path) 
        for lc in stdout.read().decode("utf8").split():
            if lc.find("init") == -1 and lc.find("agent") != -1:
                lc_log_file = lc 
        tail_log_cmd="tail -F " + lc_path+lc_log_file
        print(tail_log_cmd) 
        stdin, stdout, stderr = con.exec_command(tail_log_cmd,get_pty=True) 
        for line in iter(stdout.readline, ""):
            print(line, end="")
        con.close()
        #except:
        #    print("trying with private ip address")
            #con.connect(private_ip, username=user, pkey=k, allow_agent=False, look_for_keys=False,timeout=10)
    #except:
    #    exit()
 
if len(sys.argv) > 1:
    if(sys.argv[1]=="aws"):
        aws_lc_log()
    else:
        vm_lc_log()
else:
    vm_lc_log()