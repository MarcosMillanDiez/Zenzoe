# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 2021

@author: Marcos Millán mmillan@ubu.es
"""

from requests import get, post
from xml.etree.ElementTree import fromstring, ElementTree
from json import dumps
from time import sleep, time
from os import getcwd, makedirs


def write_data(x, y, theta, state, action_state):
    """ Writes AGV position and status data.

    Write the information obtained in "position.csv" inside the "position_history" folder.

    :param x: position on the x-axis.
    :param y: position on the y-axis.
    :param theta: orientation.
    :param state: AGV status.
    :param action_state: last order status.
    :return:
    """
    route = getcwd() + '\\position_history\\'
    route.makedirs(exist_ok=True)
    name = 'position'
    complete_route = route + name + '.csv'
    header = ['x', 'y', 'theta', 'state', 'action_state', 'time']
    data = [[x, y, theta, state, action_state, time()]]
    df = pd.DataFrame(data=np.array(data), columns=header)
    if os.path.isfile(complete_route):
        df.to_csv(complete_route, index=False, sep=';', float_format='str',
                  encoding='utf-8', decimal='.', mode="a", header=False)
    else:
        df.to_csv(complete_route, index=False, sep=';', float_format='str', encoding='utf-8', decimal='.')


def get_agv_info(zenzoe_ip):
    """ Obtains information from the AGV.

    Obtains and stores AGV information in "position.csv" inside the "position_history" folder.

    Returns x-axis position, y-axis position, orientation, status and running status.

    :param zenzoe_ip: AGV ip address.
    :return: x_pos, y_pos, theta_pos, state, action_state.
    """
    r = get("https://" + zenzoe_ip + ":8888/service/robots", auth=('admin', 'admin'), verify=False)
    root = fromstring(r.text)
    tree = ElementTree(root)
    x_pos = tree.find('robot').find('position').get('x')
    y_pos = tree.find('robot').find('position').get('y')
    theta_pos = tree.find('robot').find('orientation').text
    state = tree.find('robot').find('state').get('action')
    action_state = tree.find('robot').find('state').get('actionState')

    write_data(x_pos, y_pos, theta_pos, state, action_state)
    return x_pos, y_pos, theta_pos, state, action_state


def post_position(zenzoe_ip, x, y, ang, goal_name, zenzoe_name):
    """Send a new destination position indicating x, y and angle coordinates.

    Using the x, y coordinates and indicating the angle, we move the AGV to the indicated position.

    :param zenzoe_ip: AGV ip address.
    :param x: new position on the x-axis.
    :param y: new position on the y-axis.
    :param ang: new orientation.
    :param goal_name: goal name.
    :param zenzoe_name: AGV name.
    :return: response: shipment status.
    """
    d = {
        'type': 'GO_TO_POSITION',
        'goalName': goal_name,
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

    route = "https://" + zenzoe_ip + ":8888/service/robot/control/", zenzoe_name
    h = {'Content-Type': 'Application/json', 'Accept': 'application/json'}
    a = ('admin', 'admin')
    v = False

    response = post(route, headers=h, data=dumps(d), auth=a, verify=v)
    return response


def post_goal_name(zenzoe_ip, goal_name, zenzoe_name):
    """ Send a predefined position.

    By selecting the name of a position the AGV recognizes the coordinates and the angle at which it should move.

    :param zenzoe_ip: AGV ip address.
    :param goal_name: goal name.
    :param zenzoe_name: AGV name.
    :return: response: shipment status.
    """
    d = {
        'type': 'GO_TO_GOAL',
        'goalName': goal_name,
    }

    route = "https://" + zenzoe_ip + ":8888/service/robot/control/", zenzoe_name
    h = {'Content-Type': 'Application/json', 'Accept': 'application/json'}
    a = ('admin', 'admin')
    v = False

    response = post(route, headers=h, data=dumps(d), auth=a, verify=v)
    return response


def main():
    action = "POST_POSITION"  # type: str
    zenzoe_ip = "192.168.100.70"  # type: str
    zenzoe_name = "robot_zenzoe9"  # type: str
    goal_name = 'PARK1'  # type: str
    time_out = 5

    list_position = [[23.918, 14.364, 172.892], [23.156, 13.319, -70.829], [23.357, 12.649, -52.594],
                     [24.074, 12.264, -3.522], [24.892, 12.493, 46.084], [25.268, 13.475, 97.388],
                     [24.862, 14.212, 150.887]]  # type: List[[float ]]

    if action == "POST_POSITION":
        while 1:
            for position in list_position:
                x_pos, y_pos, theta_pos, state, action_state = get_agv_info(zenzoe_ip)  # type: str
                while action_state == "EXECUTE":
                    x_pos, y_pos, theta_pos, state, action_state = get_agv_info(zenzoe_ip)  # type: str
                if action_state == "FINISHED" or action_state == "ERROR":
                    response = post_position(zenzoe_ip, position[0], position[1], position[2], goal_name, zenzoe_name)  # type: int
                    post_time = time()
                    while response != 200 or time() - post_time >= time_out:  # We retry sending during timeout
                        response = post_position(zenzoe_ip, position[0], position[1], position[2], goal_name, zenzoe_name)  # type: int
                    sleep(2)
                while action_state == "FINISHED":
                    action_state = get_status(zenzoe_ip)  # type: str

    elif action == "POST_GOAL":
        response = post_goal_name(zenzoe_ip, goal_name, zenzoe_name)  # type: int
        post_time = time()
        while response != 200 or time() - post_time >= time_out:  # We retry sending during timeout
            sleep(0.1)
            response = post_goal_name(zenzoe_ip, goal_name, zenzoe_name)  # type: int

        x, y, ang, state, action_state = get_agv_info(zenzoe_ip)  # type: float, float, float, str, str
        while action_state == "EXECUTE":
            print 'action state: ', action_state
            x, y, ang, state, action_state = get_agv_info(zenzoe_ip)

    elif action == "GET_INFO":
        x, y, ang, state, action_state = get_agv_info(zenzoe_ip)
        print '\t- x position: ', x
        print '\t- y position: ', y
        print '\t- ang position: ', ang
        print '\t- state: ', state
        print '\t- action state: ', action_state


main()
