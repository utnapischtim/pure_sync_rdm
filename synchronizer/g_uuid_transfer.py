import os
from datetime   import date, time, datetime
from PTR_1      import PureToRdm
from setup      import upload_percent_accept, dirpath

def uuid_transfer(transfer_type):
    try:

        # Create instance
        inst_pti = PureToRdm()

        # date time in date_report.log
        current_time = datetime.now().strftime("%H:%M:%S")
        report = f"\n{str(date.today())} - {current_time}\n"
        filename = dirpath + "/reports/full_reports/" + str(date.today()) + "_report.log"
        open(filename, "a").write(report)

        # read to_transfer.log
        file_name = dirpath + '/reports/to_transfer.log'
        lines_start = sum(1 for line in open(file_name))

        retrans_data = open(file_name, 'r')
        
        uuid = retrans_data.readline()
        cnt_tot = 0
        cnt_true = 0

        print(f'{lines_start} line/s in to_transfer.log')
        
        while uuid:
            cnt_tot += 1
            print('\nuuid: ' + uuid.strip())
            
            if (len(uuid.strip()) < 36):
                print('Invalid uuid. Too short\n')
                continue

            response = inst_pti.get_pure_by_id(uuid.strip())        # calling PTR

            if response == True:        cnt_true += 1
            
            uuid = retrans_data.readline()

        lines_end = sum(1 for line in open(file_name))

        print('\n---------------------')
        if transfer_type == '':
            if cnt_tot == 0:
                print("Nothing to trasmit\n")
            else:
                print(f"Tot records: {cnt_tot} - Success transfer: {cnt_true}\n")

        else:
            if transfer_type == 'full_comp':
                report = f"\nFull comparison - {date.today()} - "

            elif transfer_type == 'update':
                report = f"\nUpdate - {date.today()} - "

            elif transfer_type == 'changes':
                report = f"\nChanges - {date.today()} - "

            if cnt_tot == 0:
                report += "success\nNothing to trasmit\n"
            else:
                percent_success = cnt_true * 100 / cnt_tot

                if percent_success >= upload_percent_accept:
                    report += "success\n"
                else:
                    report += "error\n"

                current_time = datetime.now().strftime("%H:%M:%S")
                report += f"{current_time}\nTot records: {cnt_tot} - Success transfer: {cnt_true}\nLines start: {lines_start} - Lines end: {lines_end}\n\n"
            
            open(dirpath + '/reports/d_daily_updates.log', "a").write(report)
            print(report)

    except:
        print('\n---   !!!   Error in 2_uuid_transmit.py   !!!   ---\n')

# uuid_transfer('')