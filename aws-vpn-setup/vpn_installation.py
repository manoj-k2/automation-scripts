import paramiko
import os
import subprocess
from scp import SCPClient

work_dir = os.getcwd()
home_dir = os.path.expanduser('~')

# set basic configs
def set_config():
    global work_dir,public_ip,config_file,private_ip,user,vpn_username,vpn_password,pem_file,service_file_data
    public_ip = "18.191.247.91"
    private_ip = "172.31.27.146"      # Optional
    user = "ubuntu"
    vpn_username="manojy"             # username
    vpn_password="$0x0o9Ac!FR&E"      # password
    pem_file = home_dir+"/Downloads/k2-qa.pem"
    config_file = home_dir+"/Downloads/Manojy-K2io-OpenVPN.ovpn"
    service_file_data="[Unit]\nDescription=OpenVPN Robust And Highly Flexible Tunneling Application\nAfter=network.target\n\n[Service]\nType=notify\nPrivateTmp=true\nExecStart=/usr/sbin/openvpn --cd /etc/openvpn/ --config k2io-openvpn-viscosity-config.conf\n\n[Install]\nWantedBy=multi-user.target\n"

# copy openVPN file from download to work_dir and update it 
def create_vpn_config_file():
    copy_cmd = "cp  "+config_file+" "+work_dir+"/openvpn-config"
    subprocess.run(copy_cmd, shell=True)
    # Change "auth-user-pass" line to  "auth-user-pass /etc/openvpn/credentials" 
    f = open("openvpn-config", "r")
    vpn_data = f.readlines()
    f.close()
    count=0
    for line in vpn_data:
        if line.find("auth-user-pass") != -1:
            vpn_data[count] = "auth-user-pass /etc/openvpn/credentials\n"
        count+=1
    f = open("openvpn-config", "w")
    f.writelines(vpn_data)
    f.close()

# creates service and credentials files
def create_service_file():
    f = open("service", "w")
    f.writelines(service_file_data)
    f.close() 
    print("\033[1;33mCreated openvpn-setup files\n\033[0m")

def create_cred_file():
    f = open("credentials", "w")
    cred_data=vpn_username+"\n"+vpn_password+"\n"
    f.writelines(cred_data)
    f.close() 

# Connection to aws instance using private IP 
def aws_connection():
    def copy_files():
        con.exec_command("mkdir vpn")
        with SCPClient(con.get_transport()) as scp:
            scp.put("openvpn-config", "~/vpn/k2io-openvpn-viscosity-config.conf")
            scp.put("credentials", "~/vpn/credentials")
            scp.put("service", "~/vpn/service")
        make_vpn = "sudo rm -rf /etc/openvpn/; sudo mkdir /etc/openvpn/"
        stdin , stdout, stderr =con.exec_command(make_vpn)
        print(stderr.read().decode("utf8")) 
        cp_config="sudo cp ~/vpn/k2io-openvpn-viscosity-config.conf /etc/openvpn/"
        cp_cred="sudo cp ~/vpn/credentials /etc/openvpn/"
        cp_service="sudo cp ~/vpn/service /lib/systemd/system/openvpn-edited.service"
        print("\033[1;33m\nCopying Files to aws instance...\033[0m")
        con.exec_command(cp_config)
        print("k2io-openvpn-viscosity-config.conf copied")
        con.exec_command(cp_cred)
        print("credentials copied")
        con.exec_command(cp_service)
        print("openvpn-edited.service copied\n")
        con.exec_command("rm -rf vpn")


    def install_ovpn():
        try:
            print("\033[1;33minstalling openvpn...\033[0m")
            cmd="sudo apt-get -y install openvpn unzip"
            stdin , stdout, stderr =con.exec_command(cmd,get_pty=True)
            print(stdout.read().decode("utf8")) 
            for line in iter(stdout.readline, ""):
                print(line, end="")
        except:
            print("error in installing openvpn client")
            print("please install open-vpn client manually")

# Start the open-vpn service
    def start_service():
        print("\033[1;33mStarting services...\033[0m")
        service_enable = "sudo systemctl enable openvpn-edited.service"
        service_start = "sudo systemctl start openvpn-edited.service"
        service_status = "sudo systemctl status openvpn-edited.service"
        print("service status:")
        stdin , stdout, stderr = con.exec_command(service_enable)
        print(stderr.read().decode("utf8"))
        stdin , stdout, stderr = con.exec_command(service_start)
        print(stderr.read().decode("utf8"))
        stdin , stdout, stderr = con.exec_command(service_status)
        print(stderr.read().decode("utf8"))
        print(stdout.read().decode("utf8"))

# check vpn connectivity to other vm   
    def test_vpn():
        print("\033[1;33mchecking VPN...\033[0m")
        check_vm = "ping -c 5 192.168.5.68"
        stdin , stdout, stderr = con.exec_command(check_vm)
        print(stderr.read().decode("utf8"))
        #print(stdout.read().decode("utf8"))
        if stdout.read().decode("utf8").find("100% packet loss") !=-1:
            print("Could not ping 192.168.5.68")
            print("\033[1;31m\nVPN COULD NOT STARTED !!\033[0m\n")
        else:
            print("\033[1;32mVPN STARTED SUCCESSFULLY\033[0m\n")

### starting connections
    print("Connecting to aws instance...")
    try:
        con = paramiko.SSHClient()   
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        k = paramiko.RSAKey.from_private_key_file(pem_file)
        con = paramiko.SSHClient()
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:   
            con.connect(public_ip, username=user, pkey=k, allow_agent=False, look_for_keys=False,timeout=10)   
        except:
            print("trying with private ip address")
            con.connect(private_ip, username=user, pkey=k, allow_agent=False, look_for_keys=False,timeout=10)
    except:
        print("\033[1;31mCould not connected to instance !\033[0m")
        exit()
    print("\033[1;32mConnection stablished to "+public_ip+"\033[0m")

    copy_files()
    install_ovpn()
    start_service()
    test_vpn()    
    
# -------------------

print("\033[1;36m\nOpenVPN INSTALLATION FOR AWS INSTANCE\033[0m\n")
set_config()
create_vpn_config_file()
create_service_file()
create_cred_file()
aws_connection()
