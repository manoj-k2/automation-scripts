# Open-VPN Auto-Installation script
- It can install VPN on AWS instances from your machine (Mac)

### Steps to setup VPN
- Clone the latest repository from GitHub on your with-LC machine:
  ```
  git clone https://github.com/manoj-k2/automation-scripts.git
  ```
  
- Go inside the directory :
    ```sh
    cd automation-scripts/aws-vpn-setup/
    ```

- Install Python3 on your machine and install these modules : 
    ```sh
    pip3 install -U pip setuptools 
    pip3 install paramiko
    pip3 install scp
    ```

- Edit set_config() method according to your configurations in the script:
    ```sh
    Mandatory fields: 
    - public_ip
    - user
    - vpn_username
    - vpn_password
    - pem_file
    - config_file
    ```

- Run script on your machine:
    ```sh
    python3 vpn_installation.py 
    ```
- NOTE: IF it fails, install Open-VPN client on machine by manually:
- https://www.ovpn.com/en/guides/ubuntu-cli