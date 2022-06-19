import OperationsReport

OperationsReport.set_config()
OperationsReport.validator_check()
OperationsReport.microagent_check()
#OperationsReport.get_rss_file("with")
#OperationsReport.get_rss_file("without")
OperationsReport.get_cpu_result()
OperationsReport.get_memory_result()
OperationsReport.show_result()
OperationsReport.show_graph()
OperationsReport.compare_with_old()
OperationsReport.save_to_reports()
