# Longevity autorun 
- This script can run longevity test for following LCs: (on k2 private cloud)
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

- Install Python3 on your machine and install the module paramiko:
    ```sh
    pip3 install -U pip setuptools 
    pip3 install paramiko
    ```

- Edit config.json file according to longevity configuration:
    ```sh
    vi config.json

    Note: you can take reference for your respective LC from:
    cat lc_config/{your_lc}_config.json
    ```

- Run longevity on with-machine:
    ```sh
    python3 longevity_automation_script.py 
    ```

- Please verify test on instana graph : 
    ```sh
    https://instana.io/s/lfTNWLz-QA-VhSv8RBwq7w
    ```
    