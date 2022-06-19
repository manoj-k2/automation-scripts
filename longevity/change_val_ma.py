import os
import sys

f = open("/root/manoj/longevity/config.json", "r")
data = f.readlines()
f.close()
count=0
for line in data:
    if line.find('"validator":') != -1:
        data[count] = '    "validator": "'+sys.argv[1]+'",\n'
        print(data[count])
    elif line.find('"microagent":') != -1:
        data[count] = '    "microagent": "'+sys.argv[2]+'",\n'
        print(data[count]) 
    count+=1
f = open("/root/manoj/longevity/config.json", "w")
f.writelines(data)


# add this function to your ~/.bashrc file
# config(){
#  python3 /root/manoj/change_val_ma.py $1 $2;
# }
# run:  config 650 230