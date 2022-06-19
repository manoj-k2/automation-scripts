import paramiko

# connection to aws instance using private IP 
con = paramiko.SSHClient()   
con.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
k = paramiko.RSAKey.from_private_key_file("/Users/k2cyber/Downloads/k2-qa.pem")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("192.168.30.5", username="fedora", pkey=k, allow_agent=False, look_for_keys=False)

stdin , stdout, stderr = c.exec_command("ls")
print(stdout.read().decode("utf8"))
print(stderr.read().decode("utf8"))
