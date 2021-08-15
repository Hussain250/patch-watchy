import time
import sys 
import os
from multiprocessing import Process, Manager
import math

def get_bytes(t, iface='wlp2s0'):
    with open('/sys/class/net/' + iface + '/statistics/' + t + '_bytes', 'r') as f:
        data = f.read();
        return int(data)

def conversion(diff_val):
    round_to = 1
    final_string=""
    if (diff_val > 1048576):
        fmt_val = (diff_val / 1048576.0) * 8 
        final_string = str(round(fmt_val, round_to)) + " Mb/s"
    elif(diff_val > 1024):
        fmt_val = (diff_val / 1024.0) * 8
        final_string = str(round(fmt_val, round_to)) + " Kb/s"
    else:
        fmt_val = diff_val * 8
        final_string = str(round(fmt_val, round_to)) + " b/s"
    return final_string



def convert_size(size_bytes):
    round_to = 1
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, round_to)
    return "%s %s" % (s, size_name[i])

def get_all_speeds():
    manager = Manager()
    all_speed = manager.dict()
    all_aggr_upload = manager.dict()
    all_aggr_download = manager.dict()
    all_con_aggr_upload = manager.dict()
    all_con_aggr_download = manager.dict()
    all_ifaces = ['net0','net1','net2','net3','net4','net5','net6','net7']
    proc = []

    def get_interface_speed(iface):
        tx1 = get_bytes('tx', iface)
        rx1 = get_bytes('rx', iface)
    
        time.sleep(1)
    
        tx2 = get_bytes('tx', iface)
        rx2 = get_bytes('rx', iface)
    
        tx_diff = tx2 - tx1
        rx_diff = rx2 - rx1
        all_aggr_upload[iface] = tx_diff
        all_aggr_download[iface] = rx_diff

        all_con_aggr_upload[iface] = tx2
        all_con_aggr_download[iface] = rx2

        tx_speed = conversion(tx_diff)
        rx_speed = conversion(rx_diff)

        tx_consumed = convert_size(tx2)
        rx_consumed = convert_size(rx2)
        final_result = { "upload": tx_speed, "download": rx_speed, 'consumed_upload': tx_consumed, 'consumed_download': rx_consumed}
        all_speed[iface] = final_result


    for each_interface in os.listdir("/sys/class/net"):
        if ("net" in each_interface):
            p = Process(target=get_interface_speed, args=(each_interface,))
            p.start()
            proc.append(p)
    
    for p in proc:
        p.join()
    
    for iface in all_ifaces:
        if not(iface in all_speed):
            all_speed[iface] = {'download': '0.0 b/s', 'upload': '0.0 b/s', 'consumed_upload': '0 B', 'consumed_download': '0 B'}

    final_upload = 0.0
    final_download = 0.0

    final_con_upload = 0.0
    final_con_download = 0.0

    for ind_upload in all_aggr_upload.keys():
	final_upload+= all_aggr_upload[ind_upload]
    for ind_download in all_aggr_download.keys():
	final_download+= all_aggr_download[ind_download]



    for ind_upload in all_con_aggr_upload.keys():
	final_con_upload+= all_con_aggr_upload[ind_upload]
    for ind_download in all_con_aggr_download.keys():
	final_con_download+= all_con_aggr_download[ind_download]

    all_speed['all'] = { 'download': conversion(final_download), 'upload': conversion(final_upload), 'consumed_upload': convert_size(final_con_upload), 'consumed_download': convert_size(final_con_download)}
    return all_speed.copy()

#print(get_all_speeds())
