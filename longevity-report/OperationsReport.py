import os
import subprocess
import json
import sys
import time
from termcolor import colored
import paramiko 
import numpy as np
import matplotlib.pyplot as plt
from scp import SCPClient
from subprocess import check_output

work_dir = os.getcwd() 
home_dir= os.path.expanduser('~')
def set_config():
    global validator_endpoint, without_machine, with_machine,machine_password,validator,microgent,app_name
    global with_cpu,without_cpu, overhead_cpu, overhead_cpu_per,report_time,all_reports_dir
    with_cpu=""
    without_cpu=""
    overhead_cpu=""
    overhead_cpu_per="" 
    validator=""
    microgent=""
    app_name=""
    try:
        file = open("config.json", "r")
        config = json.loads(file.read())
        with_machine = config["with_machine"]
        without_machine = config["without_machine"]
        machine_password = config["machine_password"]
        validator_endpoint = config["validator_endpoint"]
        temp=config["report_duration_hr"]
        if temp !="":
            report_time=int(temp)
        else:
            report_time=0
        #without_cpu=config["without_cpu"]
        #with_cpu=config["with_cpu"]
        file.close()
        all_reports_dir=os.path.expanduser('~')+"/Desktop/all_longevity_reports/"
    except:
        print("\033[1;31m\nError occurred in config.json file !\033[0m\n")
        quit() 

def validator_check():
    print(colored("validator checking","yellow"))
    global validator
    if validator_endpoint=="":
        ssh=with_machine
    else:
        ssh=validator_endpoint
    try:
        con = paramiko.SSHClient()   
        # con.load_system_host_keys("/root/.ssh/known_hosts") 
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
        con.connect(ssh, username="root", password=machine_password)
        #print("Validator finding : ",ssh) 
        stdin, stdout, stderr = con.exec_command("docker ps")
        #print(stdout.read().decode("utf8"))
        for line in stdout.read().decode("utf8").split("\n"):
            if line.find("validator") != -1:
                validator=line.split()[1].split(":")[-1]
        con.close()
    except:
        print("Validator could not found !")

def microagent_check():
    print(colored("microagent checking","yellow"))
    global microgent,app_name
    try:
        con = paramiko.SSHClient()   
        # con.load_system_host_keys("/root/.ssh/known_hosts") 
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
        con.connect(with_machine, username="root", password=machine_password)
        #print("Micro-Agent finding : ",with_machine) 
        stdin, stdout, stderr = con.exec_command("docker ps")
        for line in stdout.read().decode("utf8").split("\n"):
            if "k2-micro-agent" in line:
                microgent=line.split()[1].split(":")[-1]
            elif line and "instana/agent" not in line and "IMAGE" not in line and "k2-db" not in line and "k2-validator" not in line:
                #print(line)
                app_name=line.split()[1].split(":")[-1]
        con.close()
    except:
        print("microgent could not found !") 

def get_rss_file_66():
        print(colored("without rss file copying...","yellow"))
    #try:
        con = paramiko.SSHClient()   
        # con.load_system_host_keys("/root/.ssh/known_hosts") 
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
        con.connect("192.168.5.68", username="root", password=machine_password)
        vmtransport=con.get_transport()
        dest=('192.168.5.66',22)
        local=('192.168.5.68',22) 
        vmchannel=vmtransport.open_channel("direct-tcpip",dest,local)
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        ssh1.connect("192.168.5.66", username="root", password=machine_password,sock=vmchannel,timeout=60)
        cmd="hostname -I | awk '{print $1}'"
        stdin,stdout,stderr = ssh1.exec_command(cmd)
        #print("connected to vm:",stdout.read().decode("utf8"))
        file_path="/root/longevity-report/"
        ssh1.exec_command("mkdir "+file_path)
        ssh1.exec_command("docker cp ruby:/syscalls_ruby/rss_longevity.txt "+file_path)
        #print("copied from container.")
        copy_to_vm = "scp root@192.168.5.66:"+file_path+"rss_longevity.txt "+file_path
        con.exec_command(copy_to_vm)
        #print("copied from 66 to 68") 
        # Using sftp for copy metho
        sftp = con.open_sftp()
        sftp.get(file_path+"rss_longevity.txt", work_dir+"/rss_longevity.txt")
        sftp.close()
        # using SCP Client method 
        #with SCPClient(con.get_transport(),socket_timeout=60) as scp:
        #    scp.get(file_path+"rss_longevity.txt", work_dir+"/")
        cmd= "sed 's/ /,/g' rss_longevity.txt > rss_without.csv"
        subprocess.run(cmd,shell=True)
        con.close()
    #except:
    #    print("ERROR: Could not perform rss file operation on 192.168.5.66 VM")
    #    exit()

def get_rss_file(machine):
    if machine=="with":
        ssh = with_machine
    else:
        ssh = without_machine 
    if ssh=="192.168.5.66":
       get_rss_file_66() 
       return
    try:
        print(colored("with rss file copying...","yellow"))
        os.chdir(work_dir)
        con = paramiko.SSHClient()   
        # con.load_system_host_keys("/root/.ssh/known_hosts") 
        con.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        # print(ssh,machine_password)
        con.connect(ssh, username="root", password=machine_password)
        #print("Getting rss file from Machine: ",ssh) 
        file_path="/root/longevity-report/"
        con.exec_command("mkdir "+file_path)
        con.exec_command("docker cp ruby:/syscalls_ruby/rss_longevity.txt "+file_path)
        with SCPClient(con.get_transport()) as scp:
            scp.get(file_path+"rss_longevity.txt", work_dir+"/")
        cmd= "sed 's/ /,/g' rss_longevity.txt > rss_"+machine+".csv"
        subprocess.run(cmd,shell=True)
        con.close()
    except:
        print("ERROR: Could not perform rss file operation on "+machine)
        exit()

# MEMORY RESULTS
def get_memory_result():
    print(colored("getting memory result...","yellow"))
    global avg_without_memory,avg_with_memory,memory_overhead,memory_overhead_per,x,y,z,report_time
    x=[]
    y=[]
    z=[]
    os.chdir(work_dir)
    file = open("rss_without.csv", "r")
    data = file.readlines()
    cnt=0
    test_run_sec=report_time*3600
    for i in data:
        if report_time != 0 and cnt >= test_run_sec:
            break
        x.append(int(i.split(",")[2]))
        y.append(int(i.split(",")[1]))  
        cnt+=1
    file.close()

    file = open("rss_with.csv", "r")
    data = file.readlines()
    cnt2=0
    for i in data:
        if report_time != 0 and cnt2 >= test_run_sec:
            break
        z.append(int(i.split(",")[1]))
        cnt2+=1
    file.close()

    #print(len(y),len(z))
    if report_time == 0:
        report_time=round(cnt/3600)
    avg1=(sum(y)/1024)/len(y)
    avg2=(sum(z)/1024)/len(z)
    memory_overhead=avg2 - avg1
    memory_overhead_per="{:.1f}".format((memory_overhead/avg1)*100)
    memory_overhead=round(memory_overhead)
    avg_without_memory="{:.2f}".format((avg1/1024))
    avg_with_memory="{:.2f}".format(avg2/1024)
    subprocess.run("rm -f rss_longevity.txt",shell=True)

# CALCULATE AVERAGE CPU FROM .CSV FILE 
def get_avg_cpu(file):
    cpu= open(file, "r")
    cpu_data = cpu.readlines()
    count=1
    sum=0
    for values in cpu_data[1].split(","):
        if report_time != 0 and count >= report_time*6 :
            break
        elif count > 5:
            if float(values) <=0.08:  # check for cpu drop
                break
            sum+=float(values)
        count+=1
    cpu.close()
    run_time=round((count*10)/60)
    return((sum)/(count-5))*100,run_time

# CPU RESULTS
def get_cpu_result():
    print(colored("getting cpu result...","yellow"))
    global with_cpu,without_cpu, overhead_cpu, overhead_cpu_per,run_time,report_time
    try:
        os.chdir(home_dir+"/Downloads/")                # Path for your downloaded cpu .csv files
        ls = check_output(["ls","-th"]).decode("utf-8").split()
        file1=""
        for word in ls: 
            #print(word)
            if not file1 and word.find("metric-cpu.user") != -1:
                file1 = word
            elif word.find("metric-cpu.user") != -1:
                file2 = word
                break
        if not file1 or not file2: 
            print("CPU graph files are not found at location: ~/Downloads/")
            print("Please download these files from instana graph. File name eg: metric-cpu.user_usage_normalized.csv")
            #exit() 
        #print(file1,file2)
        average_cpu1,run_time = get_avg_cpu(file1) 
        average_cpu2,run_time = get_avg_cpu(file2)  
        #print(report_time,run_time)  
        if report_time == 0:
            report_time=run_time
        else:
            report_time=min(report_time,run_time)
        #print(average_cpu1,average_cpu2)
        if average_cpu2 > average_cpu1:
            with_cpu=average_cpu2
            without_cpu=average_cpu1
        else:
            without_cpu=average_cpu2
            with_cpu=average_cpu1 
        overhead_cpu = with_cpu - without_cpu
        overhead_cpu_per="{:.1f}".format((overhead_cpu/without_cpu)*100) 
        overhead_cpu= "{:.1f}".format(overhead_cpu)
        with_cpu="{:.1f}".format(with_cpu)
        without_cpu="{:.1f}".format(without_cpu)
    except:
        print(colored("ERROR: CPU Result could not calculated ! Ensure that cpu graph files are present in ~/Downloads directory","red"))
        #exit()

def show_result():
    print("\033[1m")
    output=""
    output+="Ruby agent:\n"
    output+="==========\n\n"
    output+="Validator Build used: "+validator+"\n"
    output+="MA build used: "+microgent+"\n"
    output+="Test Config: 100 requests/sec for " +str(report_time)+" hours\n"
    output+="Application Server: Unicorn\n"
    output+="Application name:"+app_name+"\n"
    output+="\n\n     Memory (Resident)\n"
    output+="     =================\n"
    output+="     Max usage with K2: "+str(avg_with_memory)+" GiB\n"
    output+="     Max usage without K2: "+str(avg_without_memory)+" GiB\n"
    output+="     Overhead: "+str(memory_overhead)+" MiB\n"
    output+="     Overhead %: ("+str(memory_overhead)+"/"+str(avg_without_memory)+"*1024))*100 = "+str(memory_overhead_per)+"% (approx.)\n"
    output+="\n\n     CPU (User) \n"
    output+="     =========\n"
    output+="     Normalized CPU usage with K2: "+str(with_cpu)+"%\n"
    output+="     Normalized CPU usage without K2: "+str(without_cpu)+"%\n"
    output+="     Overhead: "+str(overhead_cpu)+"%\n"
    output+="     Overhead %: ("+str(overhead_cpu)+"/"+str(without_cpu)+")*100 = "+str(overhead_cpu_per)+"% (approx.)\n"
    print(output,"\033[0m")
    subprocess.run("mkdir "+work_dir+"/output",stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL,shell=True)
    f = open(work_dir+"/output/Longevity", "w")
    f.writelines(output)
    f.close() 

def show_graph():
    a=np.array(x)
    b=np.array(y)
    c=np.array(z)
    if len(b) > len(c):
        b=b[len(b)-len(c):]
        a=a[len(a)-len(c):]
    else:
        c=c[len(c)-len(b):]
    # plotting
    plt.title("Line graph")
    plt.xlabel("Time")
    plt.ylabel("RSS Memory (in GB)")
    plt.ylim(bottom=1000000, top=3500000)
    #plt.subplot2grid((11,1), (0,0), rowspan = 3, colspan = 1)
    plt.plot(a, b, color ="blue", label='without-ruby-agent')
    plt.plot(a, c, color ="red", label='with-ruby-agent')
    plt.legend(loc='lower right')
    plt.savefig(work_dir+"/output/RUBY-Memory.png")
    plt.show()

def show_cpu_graph():
    a=np.array(x)
    b=np.array(y)
    c=np.array(z)
    if len(b) > len(c):
        b=b[len(b)-len(c):]
        a=a[len(a)-len(c):]
    else:
        c=c[len(c)-len(b):]
    # plotting
    plt.title("Line graph")
    plt.xlabel("Time")
    plt.ylabel("RSS Memory (in GB)")
    plt.ylim(bottom=1000000, top=3500000)
    #plt.subplot2grid((11,1), (0,0), rowspan = 3, colspan = 1)
    plt.plot(a, b, color ="blue", label='without-ruby-agent')
    plt.plot(a, c, color ="red", label='with-ruby-agent')
    plt.legend(loc='lower right')
    plt.savefig(work_dir+"/output/RUBY-Memory.png")
    plt.show()

def compare_with_old():
        global validator
    #try:
        old_reports_dir = check_output(["ls","-th",os.path.expanduser('~')+"/Desktop/all_longevity_reports/"]).decode("utf-8").split()
        if(validator == ""):
            validator = input("please input validator version: ")
        else:
            validator = validator.split("-")[-1]
        if old_reports_dir[0] == validator:
            old_report = old_reports_dir[1]
        else:
            old_report = old_reports_dir[0] 
        data= open(all_reports_dir+old_report+"/Longevity", "r").readlines()
        cpu=0
        #print(old_report)
        for line in data:
            if line.find("Validator Build used") !=-1:
                old_val=line.split()[-1]
            elif line.find("MA build") !=-1:
                old_ma=line.split()[-1]
            elif line.find("CPU") !=-1:
                cpu=1
            elif line.find("Memory") !=-1:
                cpu=0
            elif line.find("Overhead") != -1 and line.find("MiB") != -1:
                old_memory_overhead=line.split()[-2]
            elif line.find("Overhead %") != -1:
                if(cpu==0):
                    old_memory_overhead_per=line.split()[-2]
                else:
                    old_cpu_overhead_per=line.split()[-2] 
        #print(old_memory_overhead,old_memory_overhead_per,old_cpu_overhead_per)
        print(colored("\nComparing the result with old report: ","yellow"),old_val,",",old_ma)
        compare_result="                  Memory Overhead              Memory overhead %           CPU overhead %\n"
        compare_result+="Ruby-Agent        "+str(memory_overhead)+" MiB / "+old_memory_overhead+" MiB"
        compare_result+="               "+str(memory_overhead_per)+"% / "+old_memory_overhead_per
        compare_result+="              "+str(overhead_cpu_per)+"% / "+old_cpu_overhead_per 
        print(compare_result)
    #except:
    #    print("Could not find old report !")


def save_to_reports():
    save=input("\nDo you want to save this report to all longevity reports directory:(y/n): ")
    if(save != "y"):
        return
    new_dir=all_reports_dir + validator
    subprocess.run("mkdir "+new_dir,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL, shell=True) 
    cp_cmd="cp -r output/ "+new_dir
    subprocess.run(cp_cmd, shell=True)
    print(colored("Report saved at path: ","yellow"),colored(new_dir,"yellow"),"\n")
