import json
import os
import subprocess
import sys
from flask import Flask
from flask import send_from_directory
from flask import request, make_response, jsonify, redirect, url_for
from flask.json import JSONDecoder
from flask.templating import render_template
import interface_manager
import net_speed
import ui_logger
import subprocess
from ui_logger import uilogger
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
import liaison_client
from werkzeug import secure_filename

remote_path = '/tmp/update/update.status'

# ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static')
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, '/static/upload/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
global log_filename

INSTALL_UPLOAD_FOLDER = '/tmp/local_update/'
app.config['INSTALL_UPLOAD_FOLDER'] = INSTALL_UPLOAD_FOLDER
#maxwell_servers = [
#   {"id": "blr01", "location": "Bangalore", "domain": "maxblr01.watchy.in"},
#   {"id": "bom01", "location": "Mumbai", "domain": "maxbom01.watchy.in"},
#   {"id": "del01", "location": "Delhi", "domain": "maxdel01.watchy.in"}]
import ConfigParser
import sys

CORE_CONFIG_PATH="/opt/watchy/bond007-core/conf/maxwell.cfg"
coreconfigfile = ConfigParser.ConfigParser()
coreconfigfile.read(CORE_CONFIG_PATH)
server_domain = [ x for x in coreconfigfile.get("all_maxwells", "domain").split(" ") if x ]
server_location = [ x for x in coreconfigfile.get("all_maxwells", "location").split(" ") if x ]
server_id = [ x for x in coreconfigfile.get("all_maxwells", "id").split(" ") if x ]

all_servers_dict = []
for each_domain,each_location,each_id in zip(server_domain, server_location, server_id):
    all_servers_dict.append({"id": each_id, "location": each_location, "domain": each_domain})

maxwell_servers = all_servers_dict
#[all_maxwells]
#domain = maxblr01.watchy.in maxbom01.watchy.in maxdel01.watchy.in 
#location  = Bangalore Mumbai Delhi 
#id = blr01 bom01 del01

 

@app.route("/")
def dial_page():
    dongle_name = [
        {"display_name": "1", "id": "dongle0"},
        {"display_name": "2", "id": "dongle1"},
        {"display_name": "3", "id": "dongle2"},
        {"display_name": "4", "id": "dongle3"},
        {"display_name": "5", "id": "dongle4"},
        {"display_name": "6", "id": "dongle5"},
        {"display_name": "7", "id": "dongle6"},
        {"display_name": "8", "id": "dongle7"}]
    operator_2g = [
        {"id": "aircel-2g", "display_name": "Aircel"},
        {"id": "airtel-2g", "display_name": "Airtel"},
        {"id": "bsnl-2g", "display_name": "BSNL"},
        {"id": "idea-2g", "display_name": "Idea"},
        {"id": "mts-2g", "display_name": "MTS"},
        {"id": "tataphoton-2g", "display_name": "Tata Photon+"},
        {"id": "reliance-2g", "display_name": "Reliance"},
        {"id": "vodafone-2g", "display_name": "Vodafone"}]
    operator_3g = [
        {"id": "aircel-3g", "display_name": "Aircel"},
        {"id": "airtel-3g", "display_name": "Airtel"},
        {"id": "bsnl-3g", "display_name": "BSNL"},
        {"id": "idea-3g", "display_name": "Idea"},
        {"id": "mts-3g", "display_name": "MTS"},
        {"id": "tatadocomo-3g", "display_name": "Tata Dococmo"},
        {"id": "reliance-3g", "display_name": "Reliance"},
        {"id": "vodafone-3g", "display_name": "Vodafone"}]
    msg = {}
    msg["action"] = "GET_VERSION"
    interface_manager.send_to(None, msg)
    return render_template('dial_page.html', dongle_name=dongle_name, operator_2g=operator_2g, operator_3g=operator_3g, maxwell_servers=maxwell_servers)


@app.route("/update")
def update_page():
    pass


@app.route("/uploaded_file")
def fileload():
    uilogger.debug('download')


@app.route("/test/")
def test():
    return send_from_directory(app.config['UPLOAD_FOLDER'], '/static/log.tar.gz', as_attachment=True)


@app.route("/connection_manager/connect_wifi", methods=['POST'])
def connect_wifi():
    return 0


@app.route("/changeServer", methods=['POST'])
def changeServer():
    print("---------------------------------")
    print(request.json)
    os.system("/opt/watchy/bond007-ui/scripts/change_server.sh " + request.json['server'])
    print("---------------------------------")
    return json.dumps(request.json)


@app.route("/getServer", methods=['POST'])
def getServer():
    print("---------------------------------")
    CORE_CONFIG_PATH="/opt/watchy/bond007-core/conf/maxwell.cfg"
    coreconfigfile = ConfigParser.ConfigParser()
    coreconfigfile.read(CORE_CONFIG_PATH)
    server = coreconfigfile.get("maxwells", "list")
    for each_server in maxwell_servers:
        if (each_server.get("domain") == server):
            return json.dumps({ "server" : each_server.get("location") })
    print(server)
    print("---------------------------------")
    return json.dumps({ "server" : server })





@app.route("/connection_manager/get_state", methods=['POST'])
def get_state():
    dongle_name = request.json['dongle_name']
    # interface_manager.sendToAll('GET_DEVICE_INFO')
    state = interface_manager._curr_state
    return jsonify(state=state)

@app.route("/connection_manager/get_curr_usage", methods=['POST'])
def get_curr_usage():
    interface_manager.getSpeed()
    interface_manager.getDataUsage()
    uilogger.debug(interface_manager.usage)
    return json.dumps(interface_manager.usage)


@app.route("/connection_manager/get_individual_speed", methods=['POST'])
def get_individual_speed():
    interface_manager.get_individual_speed()
    uilogger.debug(interface_manager.speed)
    return json.dumps(interface_manager.speed)

@app.route("/connection_manager/get_individual_speeds", methods=['POST'])
def get_individual_speeds():
    all_speeds = net_speed.get_all_speeds()
    return json.dumps(all_speeds)


@app.route("/connection_manager/get_curr_usage_log", methods=['POST'])
def get_curr_usage_log():
    log = interface_manager.get_leased_ip()
    return json.dumps(log)


@app.route("/connection_manager/get_curr_dongle_state", methods=['POST'])
def curr_dongle_attri():
    update = True
    return jsonify(dongle=interface_manager.ui_dongle_info)


@app.route("/connection_manager/get_version", methods=['POST'])
def get_version():
    version = interface_manager.get_watchy_app_bundle_version()
    uilogger.debug(version)
    versions = {"watchy_app": version}
    return json.dumps(versions)


@app.route("/connection_manager/get_serial_number", methods=['POST'])
def get_serial_number():
    serial_number = interface_manager.get_serial_number()
    uilogger.debug(serial_number)
    serial_number_json = {"serial_number": serial_number}
    return json.dumps(serial_number_json)


@app.route("/connection_manager/get_balance", methods=['POST'])
def get_balance():
    interface_manager.sendToAll('GET_BALANCE')
    return json.dumps(interface_manager.balance_info, sort_keys=True)


# sends GET_DEVICE_INFO request to all the devices connected
@app.route("/connection_manager/get_device_info", methods=['POST'])
def get_device_info():
    # interface_manager.sendToAll('GET_DEVICE_INFO')
    data = 'received'
    return jsonify(data=data)

@app.route("/set_static_ip", methods=['POST'])
def set_static_ip():
    msg = None
    # msg['action'] = 'SET_STATIC_IP'
    # msg['ip'] = static_ip
    # msg['gateway'] = gateway
    # interface_manager.send_to(device_no, msg)

@app.route("/restart", methods=['POST'])
def restart():
    interface_manager.restart_device()
    return jsonify(data='restarting')


@app.route("/shutdown", methods=['POST'])
def shutdown():
    interface_manager.shutdown_device()
    return jsonify(data='shutting down')


@app.route("/log_dump", methods=['POST'])
def log_dump():
    global log_filename
    uilogger.info('calling dump log')
    dumplog = 'dump_log'
    log_filename = interface_manager.dump_log().strip()
    return jsonify(data='dumplog')


@app.route("/log_dump/download")
def log_dump_download():
    global log_filename
    uilogger.debug('download')
    return send_from_directory('/tmp', log_filename, as_attachment=True)


def isUpdate():
    update_state = False
    uilogger.debug('Checking if update is available ' + remote_path)
    if os.path.exists(remote_path) or os.path.exists(remote_path):
        update_state = True
    else:
        update_state = False
    uilogger.debug('Update required? ' + str(update_state))
    return update_state


def start_update():
    script_path = '/opt/watchy/updater/update_script.sh'
    uilogger.debug('Calling update script application')
    get_update_process = subprocess.Popen(['bash', script_path], stdout=subprocess.PIPE)
    get_update_process.wait()
    uilogger.info(get_update_process.stdout.readline())
    cmd = "apt-cache policy watchy-app-bundle | grep -1 Installed | sed -r 's/(:|Installed: |Candidate: )//' | uniq -u | sed '$d'"
    rv = subprocess.check_output(cmd, shell=True)
    uilogger.info(cmd + ' return ' + rv)
    if not rv:
        uilogger.info('update success')
        return True
    else:
        uilogger.info('update not successfull')
        return False


def check_for_update():
    uilogger.debug('Checking for update, requesting details from server')
    script_path = '/opt/watchy/updater/update_poller.sh'
    get_check_update_process = subprocess.Popen(['bash', script_path], stdout=subprocess.PIPE)
    get_check_update_process.wait()
    uilogger.info(get_check_update_process.stdout.readline())


@app.route("/update", methods=['POST'])
def display_update():
    update_state = isUpdate()
    print update_state
    return jsonify(update=update_state)


@app.route("/download_update", methods=['POST'])
def download_update():
    uilogger.debug('download update is called')
    start_update()
    return jsonify(data='updating')


@app.route("/update_now", methods=['POST'])
def update_now():
    status = False
    update_state = isUpdate()
    if update_state:
        if start_update():
            status = True
        else:
            status = False
    return jsonify(status=status)


@app.route("/check_update", methods=['POST'])
def check_update():
    uilogger.debug('checking for updates')
    check_for_update()
    update_state = isUpdate()
    uilogger.debug('update' + str(update_state))
    return jsonify(update=update_state)


@app.route("/get_last_updated", methods=['POST'])
def get_last_updated():
    # update.status has the last updated time also last failed time.
    # This file is created by /opt/watchy/updater/updater_script.sh
    status_file = '/opt/watchy/update.status'
    cmd = 'grep "Last Updated"' + ' ' + status_file + ' | tail -n 1'
    rv = subprocess.check_output(cmd, shell=True)
    uilogger.info(cmd + ' return ' + rv)
    return jsonify(lastupdate=rv)


@app.route("/get_hotspot_details", methods=['POST'])
def get_hotspot_details():
    return jsonify(interface_manager.get_hotspot_details())


@app.route("/set_hotspot_details", methods=['POST'])
def set_hotspot_details():
    return jsonify(interface_manager.set_hotspot_details(request.json['new_ssid'], request.json['new_password']))


@app.route("/reset_hotspot_details", methods=['POST'])
def reset_hotspot_details():
    return jsonify(interface_manager.reset_hotspot_details())


@app.route("/set_hotspot_status", methods=['POST'])
def set_hotspot_status():
    hotspot_status_file_path = '/opt/watchy/bond007-core/conf/hotspot_status'
    user_message = None
    msg = {'user_message' : None}
    status = request.json['status']
    try:
        if os.path.isfile(hotspot_status_file_path):
            os.remove(hotspot_status_file_path)
        hostspot_status = 'hotspot' + ' ' + status
        with open(hotspot_status_file_path, "w+") as hotspot_status_file:
            hotspot_status_file.seek(0)
            hotspot_status_file.truncate()
            hotspot_status_file.write(hostspot_status)
        if 'off' in status:
            cmd = 'sudo service hostapd stop'
            subprocess.call(cmd, shell=True)
            uilogger.info('hostapd stopped')
        else:
            cmd = 'sudo service hostapd start'
            subprocess.call(cmd, shell=True)
            uilogger.info('hostapd started')
        user_message = "Wifi hotspot is " + status
        msg = {'user_message': user_message}
    except:
        pass
    return jsonify(msg)



@app.route("/upload_file_to_install", methods=['POST'])
def upload_file_to_install():
    if request.method == 'POST':
        upload_file = request.files['file']
        if upload_file:
            filename = upload_file.filename

            if "watchy" in filename:
                uilogger.info('upload has watchy token. saving locally')
                if not os.path.isdir(INSTALL_UPLOAD_FOLDER):
                    uilogger.info('creating local_updater dir')
                    os.mkdir(INSTALL_UPLOAD_FOLDER)
                    owner = 'vvinothkumar'
                    os.popen('chown ' + owner + ':' + owner + ' ' + INSTALL_UPLOAD_FOLDER)
                upload_file.save(os.path.join(app.config['INSTALL_UPLOAD_FOLDER'], filename))

                is_saved_locally = os.path.isfile(INSTALL_UPLOAD_FOLDER + filename)
                is_decrypted = interface_manager.is_decrypted()

                if is_saved_locally and is_decrypted:
                    uilogger.info('saved locally')
                    message = {"upload": True, "message": "Upload successful. Please click \"Install\" to proceed"}

                elif not is_saved_locally:
                    uilogger.info('file not saved')
                    message = {"upload": False, "message": "Failed to upload update."}

                elif is_saved_locally and not is_decrypted:
                    uilogger.info('not my update file')
                    message = {"upload": False, "message": "Uploaded update file is invalid."}

            else:
                message = {"upload": False, "message": "Uploaded update file is invalid."}

    return jsonify(message)


@app.route("/install_uploaded", methods=['POST'])
def install_uploaded_update():
    if interface_manager.install_uploaded_update() is True:
        message = {"install": True}
    else:
        message = {"install": False}

    return jsonify(message)


@app.route("/get_static_ip_details", methods=['POST'])
def get_static_ip_details():
    port_no = request.json['port_no']
    return jsonify(interface_manager.get_static_ip_details(port_no))


@app.route("/set_static_ip_details", methods=['POST'])
def set_static_ip_details():
    return jsonify(interface_manager.set_static_ip_details(request.json['port_no'], request.json['new_ip_address'], request.json['new_netmask'], request.json['new_gateway'], request.json['new_dns'], request.json['new_alt_dns']))


@app.route("/delete_static_ip_details", methods=['POST'])
def delete_static_ip_details():
    port_no = request.json['port_no']
    return jsonify(interface_manager.delete_static_ip_details(port_no))

# @app.route("/get_whitelist_firewall", methods=['POST'])
# def get_whitelist_firewall():
#     pass
#
# @app.route("/set_whitelist_firewall", methods=['POST'])
# def set_whitelist_firewall():
#     pass
#
# @app.route("/del_whitelist_firewall", methods=['POST'])
# def del_whitelist_firewall():
#     pass

uilogger.initialize(20)
liaison_client.initialise()
interface_manager.get_wan_port_details()

if __name__ == "__main__":
    app.run(port=int(sys.argv[2]), host=sys.argv[1])
