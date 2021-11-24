# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 2021

@author: Marcos Millán mmillan@ubu.es
"""

from requests import get, post
from requests.exceptions import Timeout, RequestException
from socket import inet_aton

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


def get_agv_info(zenzoe_ip, time_out):
    """ Obtains information from the AGV.

    Obtains and stores AGV information in "position.csv" inside the "position_history" folder.

    Returns x-axis position, y-axis position, orientation, status and running status.

    :param zenzoe_ip: AGV ip address.
    :param time_out: time we try to send the position.
    :return: x_pos, y_pos, theta_pos, state, action_state.
    """
    x_pos, y_pos, theta_pos, state, action_state = 0, 0, 0, 0, 0
    info = None
    url = "https://" + zenzoe_ip + ":8888/service/robots"
    try:
        info = get(url, auth=('admin', 'admin'), verify=False, timeout=time_out)
    except Timeout:
        print('Timeout')
    except RequestException as ex:
        print('RequestException, ', ex)
    except Exception as ex:
        print('Error in obtaining information: ', ex)

    if info is not None:
        root = fromstring(info.text)
        tree = ElementTree(root)
        x_pos = tree.find('robot').find('position').get('x')
        y_pos = tree.find('robot').find('position').get('y')
        theta_pos = tree.find('robot').find('orientation').text
        state = tree.find('robot').find('state').get('action')
        action_state = tree.find('robot').find('state').get('actionState')

        write_data(x_pos, y_pos, theta_pos, state, action_state)

        print('\t- X position: ', x_pos)
        print('\t- Y position: ', y_pos)
        print('\t- Ang position: ', theta_pos)
        print('\t- State: ', state)
        print('\t- Action state: ', action_state)

    return x_pos, y_pos, theta_pos, state, action_state


def post_fineposition(zenzoe_ip, fineposition, time_out):
    """ Indicates the AGV in which goal it is located.

    :param zenzoe_ip: AGV ip address.
    :param fineposition: Name of the goal in which it is located.
    :param time_out: time we try to send the position.
    :return: state.
    """
    data = str(fineposition)

    route = "https://" + str(zenzoe_ip) + ":8888/service/v2/command/finepos"
    headers = {'Content-Type': 'Application/json', 'Accept': 'application/json'}
    auth = ('admin', 'admin')
    verify = False
    state = 400
    try:
        response = post(route, headers=headers, data=dumps(data), auth=auth, verify=verify, timeout=time_out)
        state = response.status_code
    except Timeout:
        print('Timeout')
    except RequestException as ex:
        print('RequestException, ', ex)
    except Exception as ex:
        print('Error in obtaining information: ', ex)

    return state


def post_position(zenzoe_ip, x, y, ang, goal_name, zenzoe_name, time_out):
    """Send a new destination position indicating x, y and angle coordinates.

    Using the x, y coordinates and indicating the angle, we move the AGV to the indicated position.

    :param zenzoe_ip: AGV ip address.
    :param x: new position on the x-axis.
    :param y: new position on the y-axis.
    :param ang: new orientation.
    :param goal_name: goal name.
    :param zenzoe_name: AGV name.
    :param time_out: time we try to send the position.
    :return: response: shipment status.
    """
    data = {
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

    route = "https://" + str(zenzoe_ip) + ":8888/service/robot/control/" + str(zenzoe_name)
    headers = {'Content-Type': 'Application/json', 'Accept': 'application/json'}
    auth = ('admin', 'admin')
    verify = False
    state = 400
    try:
        response = post(route, headers=headers, data=dumps(data), auth=auth, verify=verify, timeout=time_out)
        state = response.status_code
    except Timeout:
        print('Timeout')
    except RequestException as ex:
        print('RequestException, ', ex)
    except Exception as ex:
        print('Error in sending information: ', ex)

    return state


def post_goal_name(zenzoe_ip, goal_name, zenzoe_name, time_out):
    """ Send a predefined position.

    By selecting the name of a position the AGV recognizes the coordinates and the angle at which it should move.

    :param zenzoe_ip: AGV ip address.
    :param goal_name: goal name.
    :param zenzoe_name: AGV name.
    :param time_out: time we try to send the position.
    :return: staus: shipment status.
    """
    data = {
        'type': 'GO_TO_GOAL',
        'goalName': goal_name,
    }

    route = "https://" + str(zenzoe_ip) + ":8888/service/robot/control/" + str(zenzoe_name)
    headers = {'Content-Type': 'Application/json', 'Accept': 'application/json'}
    auth = ('admin', 'admin')
    verify = False
    state = 400
    try:
        response = post(route, headers=headers, data=dumps(data), auth=auth, verify=verify, timeout=time_out)
        state = response.status_code
    except Timeout:
        print('- Timeout')
    except RequestException as ex:
        print('- RequestException, ', ex)
    except Exception as ex:
        print('- Error in sending information: ', ex)

    return state


def move_to_pos(zenzoe_ip, position_x, position_y, position_theta, zenzoe_name, time_out):
    """ We manage the sending of a new target position.

    We send a new position when the action status is "FINISHED" or a "ERROR".

    :param position_x: new position on the x-axis.
    :param position_y: new position on the y-axis.
    :param position_theta: new orientation.
    :param zenzoe_ip: AGV ip address.
    :param zenzoe_name: AGV name.
    :param time_out: time we try to send the position.
    :return:
    """

    x_pos, y_pos, theta_pos, state, action_state = get_agv_info(zenzoe_ip, time_out)  # type: str
    while action_state == "EXECUTE":
        x_pos, y_pos, theta_pos, state, action_state = get_agv_info(zenzoe_ip, time_out)  # type: str
    if action_state == "FINISHED" or action_state == "ERROR":
        response_code = post_position(zenzoe_ip, position_x, position_y, position_theta, 'goal_name_1',
                                      zenzoe_name, time_out)  # type: int
        post_time = time()
        while response_code != 200 or time() - post_time >= time_out:  # We retry sending during timeout
            response_code = post_position(zenzoe_ip, position[0], position[1], position[2], goal_name,
                                          zenzoe_name, time_out)  # type: int
            sleep(0.2)
        sleep(2)
    while action_state == "FINISHED":
        action_state = get_status(zenzoe_ip)  # type: str


def send_path(list_position, zenzoe_ip, zenzoe_name, time_out):
    """ We link a series of positions together to create a route.

    :param list_position: points trajectory.
    :param zenzoe_ip: AGV ip address.
    :param zenzoe_name: AGV name.
    :param time_out: time we try to send the position.
    :return:
    """
    for position in list_position:
        move_to_pos(zenzoe_ip, position[0], position[1], position[2], zenzoe_name, time_out)


def move_to_goal(zenzoe_ip, goal_name, zenzoe_name, time_out):
    """We manage the sending of a new goal position.

    We send a new goal position when the action status is "FINISHED" or a "ERROR".

    :param zenzoe_ip: AGV ip address.
    :param goal_name: name of the target position.
    :param zenzoe_name: AGV name.
    :param time_out: time we try to send the position.
    :return:
    """
    response_code = post_goal_name(zenzoe_ip, goal_name, zenzoe_name, time_out)  # type: int
    post_time = time()
    while response_code != 200 or time() - post_time >= time_out:  # We retry sending during timeout
        response_code = post_goal_name(zenzoe_ip, goal_name, zenzoe_name, time_out)  # type: int
        sleep(0.2)

    x, y, ang, state, action_state = get_agv_info(zenzoe_ip, time_out)  # type: float, float, float, str, str
    while action_state == "EXECUTE":
        x, y, ang, state, action_state = get_agv_info(zenzoe_ip, time_out)


def check_variables(action, zenzoe_ip, zenzoe_name, goal_name, fineposition, time_out, position_x, position_y,
                    position_theta, list_position):
    """ Check value of initial variables.

    :param action: Action to be performed by AGV
    :param zenzoe_ip: AGV ip address.
    :param zenzoe_name: AGV name.
    :param goal_name: name of the target position.
    :param fineposition:
    :param time_out: time we try to send the position.
    :param position_x: new position on the x-axis.
    :param position_y: new position on the y-axis.
    :param position_theta: new orientation.
    :param list_position: points trajectory.
    :return:
    """
    assert action == "POST_POSITION" or action == "POST_PATH" or action == "POST_GOAL" or action == "GET_INFO" or\
           action == "GET_GOAL_POSITION", 'Invalid action status'
    assert type(zenzoe_ip) == str, "Variable zenzoe_ip should be a string."
    assert inet_aton("1.1.2.3"), "Ip not valid."
    assert type(zenzoe_name) == str, "Variable zenzoe_name should be a string."
    if action == "POST_GOAL":
        assert type(goal_name) == str and goal_name != '', "Variable goal_name should be a string and contain text."
    assert type(time_out) == int, "Variable time_out should be a string."
    if action == "POST_POSITION":
        assert type(position_x) == float and type(position_y) == float and type(position_theta) == float, (
            "Variable position_x, position_y, position_theta should be a float")
    if action == "POST_PATH":
        assert len(list_position) > 0, "The path doesn't contain positions."
    if action == "POST_FINEPOSITION":
        assert type(fineposition) == str and fineposition != '', (
            "Variable fineposition should be a string and contain text.")


# TODO(Marcos) create AGV class.
def main():
    # TODO(Marcos) start variables by reading a json file.
    action = "POST_FINEPOSITION"  # type: str
    zenzoe_ip = "192.168.100.70"  # type: str
    zenzoe_name = "robot_zenzoe9"  # type: str
    goal_name = "PARK1"  # type: str
    fineposition = "CHARGE_01_MG"  # type: str
    time_out = 5  # type: int
    position_x, position_y, position_theta = 23.123, 13.319, 97.388  # type: float
    list_position = [[23.918, 14.364, 172.892], [23.156, 13.319, -70.829], [23.357, 12.649, -52.594],
                     [24.074, 12.264, -3.522], [24.892, 12.493, 46.084], [25.268, 13.475, 97.388],
                     [24.862, 14.212, 150.887]]  # type: List[[float, float, float ], ...]

    check_variables(action, zenzoe_ip, zenzoe_name, goal_name, fineposition, time_out, position_x, position_y,
                    position_theta, list_position)

    if action == "POST_POSITION":
        move_to_pos(zenzoe_ip, position_x, position_y, position_theta, zenzoe_name, time_out)

    elif action == "POST_PATH":
        send_path(list_position, zenzoe_ip, zenzoe_name, time_out)

    elif action == "POST_GOAL":
        move_to_goal(zenzoe_ip, goal_name, zenzoe_name, time_out)

    elif action == "GET_INFO":
        get_agv_info(zenzoe_ip, time_out)

    elif action == "POST_FINEPOSITION":
        post_fineposition(zenzoe_ip, fineposition, time_out)


if __name__ == '__main__':
    main()
