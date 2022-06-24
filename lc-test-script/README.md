# K2 2.x Language Collector Functionality Test 
- This script can run test basic functionality for following LCs:
  - Ruby
  - Java
  - Node
  - PHP
  - Python
  - Go

- k2Agent functionalities such as: 
  - Application attachment
  - Application Info
  - get Policy
  - http-connection-stat
  - healthcheck
  - json counts
  - ERROR

### Steps to run setup
- Clone the latest repository from GitHub on your with-LC machine:
  ```
  git clone https://github.com/manoj-k2/automation-scripts.git
  ```
  
- Go inside the directory :
    ```sh
    cd automation-scripts/lc-test-script/
    ```

- Install Python3 on your machine and install the modules using script:
    ```sh
    bash modules_install.sh 
    ``` 
    or you can install manually (if fails): 
    ```sh
    pip3 install -U pip setuptools 
    pip3 install rich
    pip3 install pygments
    pip3 install pprint
    ```

- Edit config.json file:
    ```sh
    vi config.json
   
    Note:
    Provide container-name or container-id and port. 
    You can directly provide applicationUUID. 
    k2home is your k2-home directory path.
    first_data: true    - will fetch first data
    first_data: false   - will fetch last data  
    ```

- Run Script:
    ```sh
    python3 lc_test_script.py
    ```
