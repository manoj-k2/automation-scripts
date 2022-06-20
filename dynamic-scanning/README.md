# Dynamic scanning automation script
- This script can run dynamic scanning and get results for following LCs:
  - Ruby
  - Java
  - Node
  - PHP
  - Python
  - Go

### Steps to run dynamic scanning
- Clone the latest repository from GitHub on your with-LC machine:
  ```
  git clone https://github.com/manoj-k2/automation-scripts.git
  ```
  
- Go inside the directory :
    ```sh
    cd automation-scripts/dynamic-scanning/
    ```

- Edit validator and microagent version in config.json

- Edit input.json file according to your LC and application configuration:
    ```sh
    vi input.json
    ```

- Run python script:
    ```sh
    python3 dynamic_scanning_test.py 
    ```