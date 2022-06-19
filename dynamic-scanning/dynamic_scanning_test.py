import os
import OperationDS

class UtilityClass:
    ic_log_path=""
    appuid=""
    @classmethod
    def ic_config_call(self):
        work_dir = os.getcwd()
        OperationDS.set_config()
        #OperationDS.is_k2_installed()
        OperationDS.get_installer()
        OperationDS.update_agent_properties()
        OperationDS.install_k2_agent()
        ic_id = OperationDS.get_ic_id()
        UtilityClass.ic_log_path = OperationDS.k2home + "k2root/logs/int-code/" + ic_id
        print(UtilityClass.ic_log_path)
        OperationDS.set_input_config(work_dir)
    
    @classmethod
    def app_ds_call(self):
        container_name="ic-"+OperationDS.app_name
        print("\n# RUNNING APP WITH K2AGENT #\n")
        print("\nApp Name:",OperationDS.app_name)
        print("Using Policy:",OperationDS.k2_group_name)
        app_run_command = OperationDS.modify_app_command(container_name)
        print(app_run_command)
        OperationDS.remove_container(container_name)
        OperationDS.run_app(app_run_command, container_name)
        OperationDS.check_app_start(container_name)
        UtilityClass.appuid = OperationDS.get_app_uuid(container_name)
        print(UtilityClass.appuid)
        OperationDS.check_app_info(UtilityClass.appuid)
        OperationDS.find_scan_uri(container_name)
        OperationDS.start_ds(container_name)

    @classmethod
    def result_call(self):
        print("\033[1;32m\nEXPECTED VULNERABLE URIs:\033[0m\n")
        for ur in OperationDS.vulnerable_urls:
            print(ur)
        OperationDS.get_result(UtilityClass.ic_log_path, UtilityClass.appuid)
        OperationDS.match_api()
        print("\033[1;32m\nMATCHED VULNERABILITIES ->\033[0m\n")
        count1 = OperationDS.show_vulnerability(1)
        print("\033[1;31m\nVULNERABILITIES THAT ARE NOT DETECTED ->\033[0m\n")
        count2 = OperationDS.show_vulnerability(0)
        print("\033[1;31m\nDETECTED VULNERABILITIES THAT ARE NOT EXPECTED ->\033[0m\n")
        count3 = OperationDS.show_unexpected_vulnerablity()
        # Getting Conclusion
        OperationDS.conclusion(count1, count2, count3)

#   ------------   START   --------------
print("\n\033[1;33m+------------------------------------------------------------------------------+")
print("\033[1;33m|  DYNAMIC SCANNING AUTOMATION TEST SCRIPT FOR DOCKER APPLICATION ENVIRONMENT  |\033[0m")
print("\033[1;33m+------------------------------------------------------------------------------+\033[0m\n")
# Installing k2 Components
UtilityClass.ic_config_call()

# Installing the application 
UtilityClass.app_ds_call()

# Showing result 
UtilityClass.result_call()   

#    ------------     END     ------------

