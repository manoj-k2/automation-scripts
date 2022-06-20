# Longevity on Production cloud autorun (k2io.net) 
- This script generates longevity test report for following LCs:
  - Ruby
  - PHP


### Steps to run longevity
- Clone the latest repository from GitHub:
  ```
  git clone https://github.com/manoj-k2/automation-scripts.git
  ```
  
- Go inside the directory :
    ```sh
    cd automation-scripts/longevity-report/
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
    pip3 install matplotlib
    pip3 install scp
    pip3 install matplotlib
    ```

- If you want to get CPU result also: 
    ```sh
    Download CPU graph both with and without LC .csv files from instana graph into your ~/Downloads directory.
    https://instana.io/s/lfTNWLz-QA-VhSv8RBwq7w 
    
    Files path directory should be : ~/Downloads/metric-cpu.user_usage_normalized*.csv
    ```

- Edit config file according to longevity configuration:
    ```sh
    vi config.json
    
    Note: If you want to produce complete result:
    set "report_duration_hr": ""
    ```


- Run longevity-report on with-machine:
    ```sh
    python3 longevity_report.py 
    ```


    