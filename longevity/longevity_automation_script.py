import OperationsLongevity

class UtilityClass:
    @classmethod
    def with_machine_call(self):
        OperationsLongevity.remove_all()
        OperationsLongevity.get_installer()
        OperationsLongevity.update_k2_agent_file()
        OperationsLongevity.run_instana() 
        OperationsLongevity.install_k2_agent() 
        OperationsLongevity.run_app()  

    @classmethod 
    def without_machine_call(self):
        OperationsLongevity.without_machine_connection()

    @classmethod
    def app_verification(self):
        OperationsLongevity.check_app_start()
        OperationsLongevity.get_app_uuid()
        OperationsLongevity.check_app_info()
        OperationsLongevity.show_containers()
    @classmethod
    def yandex_call(self):
        OperationsLongevity.get_yandex_commands()
        OperationsLongevity.yandex_machine_connection()  
        

#   ------------   START   --------------

#print("( please run this script on APP-WITH-IC MACHINE only ) \n")
print("\n\033[1;33m+--------------------------------------------+")
print("|   LONGEVITY   TEST   AUTOMATION   SCRIPT   |")
print("+--------------------------------------------+\033[0m\n")

OperationsLongevity.set_config()
UtilityClass.with_machine_call()
UtilityClass.without_machine_call()
print("\n\033[1;32m+------------------------------------+")
print("| WITHOUT-IC MACHINE SETUP COMPLETED |")
print("+------------------------------------+\033[0m\n")
UtilityClass.app_verification()
print("\n\033[1;32m+---------------------------------+")
print("| WITH-IC MACHINE SETUP COMPLETED |")
print("+---------------------------------+\033[0m\n")
UtilityClass.yandex_call() 
print("\n\033[1;32m****  Auto-run Finished  ****\033[0m\n")
print("\033[1;33m!!! Please verify running longevity on Instana graph and K2M account !!!\033[0m\n")

#    ------------     END     ------------