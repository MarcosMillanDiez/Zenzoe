# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 16:55:31 2019

@author: Marcos Millán mmillan@ubu.es
"""

import requests
import xml.etree.ElementTree as ET
import json
import urllib3
import time
import json

# ########################################
#            VARIABLE START
# type : EMERGENCY_STOP, IDLE_MODE, AUTOMATIC_CONTROL, STOP_AUTOMATIC_CONTROL, SET_INITIAL_POSITION,
# GO_TO_POSITION, GO_TO_GOAL, GO_TO_HOME, GO_TO_DOCK, LOWLEVEL_LOAD, LOAD, LOWLEVEL_UNLOAD, UNLOAD,
# START_CHARGING, STOP_CHARGING, MAPPING_START, MAPPING_STOP, MOVE_LHD, MOVE, TURN, TURN_TO, DASH,
# START_FINE_POSITIONING, START_ESTABLISH_CLEARANCE, STOP_FINE_POSITIONING, DOCK, UNDOCK, UNCHECKED_LOAD,
# UNCHECKED_UNLOAD, PLAY_SOUND, DETECT_PALLET, CONFIRM_ALARM, SHUTDOWN, CHARGE_AND_SHUTDOWN
#
# ########################################


def get_pos(zenzoe_ip, i):
    r = requests.get("https://" + zenzoe_ip + ":8888/service/robots", auth=('admin', 'admin'), verify=False)
    root = ET.fromstring(r.text)
    tree = ET.ElementTree(root)
    x_xml = tree.find('robot').find('position').get('x')
    y_xml = tree.find('robot').find('position').get('y')
    theta_xml = tree.find('robot').find('orientation').text
    state = tree.find('robot').find('state').get('action')
    action_state = tree.find('robot').find('state').get('actionState')
    f = open('points_order_'+str(i)+'.txt', 'a+')
    f.write(str(x_xml) + " " + str(y_xml) + "\n")
    f.close()

    return x_xml, y_xml, theta_xml, state, action_state


def get_status(zenzoe_ip):
    get_x, get_y, get_ang, action, action_state = get_pos(zenzoe_ip, "zz")
    return action_state


def post_pos(zenzoe_ip, x, y, ang, goalName):
    d = {
        'type': 'GO_TO_POSITION',
        'goalName': goalName,
        'position': {
            'x': x,
            'y': y
        },
        'orientation': ang,
        'angle': 0,
        'distance': 0,
        'height': 0,
        'linear': 0,
        'angular': 0,
        'soundName': None
    }

    d1 = {
        'type': 'GO_TO_GOAL',
        'goalName': goalName,
    }

    ruta = "https://" + zenzoe_ip + ":8888/service/robot/control/robot_zenzoe9"  # + zenzoe_name
    h = {'Content-Type': 'Application/json', 'Accept': 'application/json'}
    a = ('admin', 'admin')
    v = False

    response = requests.post(ruta, headers=h, data=json.dumps(d), auth=a, verify=v)


def main():
    urllib3.disable_warnings()
    action = "POST2"  # GET_MAP   GET   POS
    zenzoe_ip = "192.168.100.70"
    zenzoe_name = "robot_zenzoe9"

    x = 33.108
    y = 9.192
    ang = -2.562
    goalName = 'PARK1'

    x = [23.918, 23.156, 23.357, 24.074, 24.892, 25.268, 24.862]
    y = [14.364, 13.319, 12.649, 12.264, 12.493, 13.475, 14.212]
    ang = [172.892, -70.829, -52.594, -3.522, 46.084, 97.388, 150.887]

    if action == "POST":
        print("POST")
        action_state = get_status(zenzoe_ip)
        while 1:
            for i in range(len(x)):
                action_state = get_status(zenzoe_ip)
                while action_state == "EXECUTE":  # EXECUTE FINISHED
                    action_state = get_status(zenzoe_ip)
                if action_state == "FINISHED" or action_state == "ERROR":
                    post_pos(zenzoe_ip, x[i], y[i], ang[i], goalName)
                    time.sleep(2)
                while action_state == "FINISHED":
                    action_state = get_status(zenzoe_ip)

    if action == "POST2":
        print("POST2")
        for i in range(len(x)):
            print "POST " + str(i)
            post_pos(zenzoe_ip, x[i], y[i], ang[i], goalName)
            pos_x, pos_y, get_ang, action, action_state = get_pos(zenzoe_ip, i)
            while (x[i] + 0.05 < float(pos_x) or float(pos_x) < x[i] - 0.5) or (
                    y[i] + 0.05 < float(pos_y) or float(pos_y) < y[i] - 0.05):
                pos_x, pos_y, get_ang, action, action_state = get_pos(zenzoe_ip, i)

            print "FIN " + str(i)
            print "sleep"
            time.sleep(1)

    if action == "GET":
        print("GET_POS")
        get_pos(zenzoe_ip)

    if action == "GET_MAP":
        print "GET_MAP: "
        get_map(zenzoe_ip)

    if action == "POST_MAP":
        print "POST_MAP"
        post_map_new_forbiden(zenzoe_ip)
        time.sleep(5)
        post_original_map(zenzoe_ip)


main()

