# Longevity autorun 
- This script can run longevity test for following LCs:
  - Ruby
  - Java
  - Node
  - PHP
  - Python
  - Go

### Steps to run longevity
- Clone the latest repository from GitHub on your with-LC machine:
  ```
  git clone https://github.com/manoj-k2/automation-scripts.git
  ```
  
- Go inside the directory :
    ```sh
    cd automation-scripts/longevity/
    ```

- Install Python3 on your machine and install these modules using bash script:
    ```sh
    bash modules_install.sh
    ```
    Or you can install it by manually : 
     ```sh
    pip install --upgrade pip
    pip3 install -U pip setuptools 
    pip3 install termcolor  
    pip3 install paramiko
    pip3 install numpy  
    pip3 install scp
    pip3 install matplotlib
    ```

- Run longevity on with-machine:
    ```sh
    python3 longevity_automation_script.py 
    ```

- Please verify test on instana graph : 
    ```sh
    https://instana.io/s/lfTNWLz-QA-VhSv8RBwq7w
    ```
    
