import os
import sys
import paramiko 


########     USER  INPUTS    #########
# For VM
vm="192.168.5.68"           

# For AWS instance
public_ip="18.191.247.91"    # if don't work please provide private ip
user="ubuntu"             

k2home="/opt/k2root/"
log_dir=k2home+"k2root/logs/int-code/"
home_dir = os.path.expanduser('~')
pem_file = home_dir+"/Downloads/k2-qa.pem"
ic_log_file="prevent_web.log"

####################################

def vm_ic_log():
    con = paramiko.SSHClient()   
    # con.load_system_host_keys("/root/.ssh/known_hosts") 
    con.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
    con.connect(vm, username="root", password="k2cyber")
    print("connected to vm: "+vm)
    stdin, stdout, stderr = con.exec_command("ls -t "+log_dir)
    appuuid=stdout.read().decode("utf8").split()[0]
    ic_path=log_dir+appuuid+"/"
    tail_log_cmd="tail -F " + ic_path+ic_log_file
    print(tail_log_cmd)
    stdin, stdout, stderr = con.exec_command(tail_log_cmd,get_pty=True) 
    for line in iter(stdout.readline, ""):
        print(line, end="")
    con.close()


def aws_ic_log():
    try:
        con = paramiko.SSHClient()   
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        k = paramiko.RSAKey.from_private_key_file(pem_file)
        con = paramiko.SSHClient()
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        con.connect(public_ip, username=user, pkey=k, allow_agent=False, look_for_keys=False,timeout=10)   
        print("connected to aws instance: "+public_ip)
        stdin, stdout, stderr = con.exec_command("ls -t "+log_dir)
        appuuid=stdout.read().decode("utf8").split()[0]
        ic_path=log_dir+appuuid+"/"
        print(ic_path)
        print(ic_log_file)
        tail_log_cmd="tail -F " + ic_path+ic_log_file
        print(tail_log_cmd) 
        stdin, stdout, stderr = con.exec_command(tail_log_cmd,get_pty=True) 
        for line in iter(stdout.readline, ""):
            print(line, end="")
        con.close()
        #except:
        #    print("trying with private ip address")
            #con.connect(private_ip, username=user, pkey=k, allow_agent=False, look_for_keys=False,timeout=10)
    except:
        exit()
 
if len(sys.argv) > 2:
        if(sys.argv[2]=="record"):
            ic_log_file="k2-vulnerability-record.log"    
        elif(sys.argv[2]=="events"):
            ic_log_file="k2-intcode_event_status.log" 
        elif(sys.argv[2]=="scanner"):
            ic_log_file="k2-vulnerability-scanner.log" 
        else:
            ic_log_file="prevent_web.log"  

if len(sys.argv) > 1:
    if(sys.argv[1]=="aws"):
        aws_ic_log()
    else:
        vm_ic_log()
else:
    vm_ic_log()

# sample run commands:
# python3 ic_log.py vm         # will tail prevent-web
# python3 ic_log.py aws 
# python3 ic_log.py vm record 
# python3 ic_log.py aws scanner
