import os
from datetime   import date, time, datetime
from PTR_1      import PureToRdm
from setup      import upload_percent_accept

try:
    dirpath = os.path.dirname(os.path.abspath(__file__))
    file_name = dirpath + '/reports/to_transfer.log'

    lines_start = sum(1 for line in open(file_name))

    # Create instance
    inst_pti = PureToRdm()

    retrans_data = open(file_name, 'r')
    
    uuid = retrans_data.readline()
    cnt_tot = 0
    cnt_true = 0
    
    while uuid:
        cnt_tot += 1
        print('\nuuid: ' + uuid.strip())
        
        if (len(uuid.strip()) < 36):
            print('Invalid uuid. Too short\n')
            continue

        response = inst_pti.get_pure_by_id(uuid.strip())

        if response == True:        cnt_true += 1
        
        uuid = retrans_data.readline()

    lines_end = sum(1 for line in open(file_name))

    print('\n---------------------')
    report = f"\n@ {date.today()} - "

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
    print('\n- Error in 2_uuid_transmit.py -\n')