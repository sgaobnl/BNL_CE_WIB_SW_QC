import components.assembly_parameter as paras
import components.assembly_log as log
import components.assembly_function as a_func


#================   Final Report    ===================================
def final_report(fembs, fembNo):
    print("\n\n\n")
    print("==================================================================================")
    print("+++++++               GENERAL REPORT for FEMB BOARDS TESTING               +++++++")
    print("+++++++                                                                    +++++++")
    print("==================================================================================")
    print("\n")
    print(log.report_log01["ITEM"])
    for key, value in log.report_log01["Detail"].items():
        print(f"{key}: {value}")

    all_true = {}
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])

        log.final_status[femb_id]["item2"] = log.report_log02[femb_id]["Result"]
        log.final_status[femb_id]["item3"] = log.report_log03[femb_id]["Result"]
        log.final_status[femb_id]["item4"] = log.report_log04[femb_id]["Result"]
        log.final_status[femb_id]["item5"] = log.report_log04[femb_id]["Result"]

        all_true[femb_id] = all(value for value in log.final_status[femb_id].values())

        if all_true[femb_id]:
            print("FEMB ID {}\t PASS\t ALL ASSEMBLY CHECKOUT".format(fembNo['femb%d'%ifemb]))
        else:
            print("femb id {}\t faild\t the assembly checkout".format(fembNo['femb%d' % ifemb]))
    print("\n\n")
    print("Detail for Issue boards")
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
        if all_true[femb_id]:
            pass
        else:
            print(femb_id)
            if log.report_log02[femb_id]["Result"] == False:
                print(log.report_log02["ITEM"])
                print(log.report_log02[femb_id])
            if log.report_log03[femb_id]["Result"] == False:
                print(log.report_log03["ITEM"])
                print(log.report_log03[femb_id])
            if log.report_log04[femb_id]["Result"] == False:
                print(log.report_log04["ITEM"])
                print(log.report_log04[femb_id])
            if log.report_log05[femb_id]["Result"] == False:
                print(log.report_log05["ITEM"])
                print(log.report_log05[femb_id])
            # if log.report_log06[femb_id]["Result"] == False:
            #     print(log.report_log06["ITEM"])
            #     print(log.report_log06[femb_id])
            if log.report_log07[femb_id]["Result"] == False:
                print(log.report_log07["ITEM"])
                print(log.report_log07[femb_id])
            if log.report_log08[femb_id]["Result"] == False:
                print(log.report_log08["ITEM"])
                print(log.report_log08[femb_id])
