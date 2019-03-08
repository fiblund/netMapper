import json
import re
from pprint import pprint

from sys import exit
from netmiko import ConnectHandler


def netmiko_conn(mgmt_ip):
    """
    :param mgmt_ip: Management IP-address of the targeted device.
    :return: Return a netmiko connection to the targeted device.
    """

    # Create a netmiko connection to the targeted IP-address using the given mgmt_ip.
    # Currently only cisco_ios is supported.
    # A standard username and password is used.
    conn_settings = {
        "ip": mgmt_ip,
        "device_type": "cisco_ios",
        "username": "gns3",
        "password": "gns3"
    }

    # Try to connect to the source device. Exit the program if it fails.
    try:
        n_conn = ConnectHandler(**conn_settings)
        n_conn.find_prompt()
    except:
        print("An error occurred!")
        exit(0)

    return n_conn


def discover_devices():
    """
    :return: Returns a list of devices in json.

    The user will input the FQDN, IP-address and device type of the source device. which will then be used to discover
    neighboring devices using CDP.
    """

    # For development purposes, the information has been entered statically.
    source_fqdn = "R1.lab"
    source_ip = "192.168.187.201"
    source_type = "cisco_ios"

    # Devices dictionary containing only the source device at start, but all devices will be added as
    # they are discovered using CDP. The key cdp_scanned is used to keep track of which devices
    # have been scanned already.
    devices = {
        source_ip:
            {
                "hostname": source_fqdn,
                "mgmt_ip": source_ip,
                "type": source_type,
                "cdp_scanned": False
            }
        }

    # Used to check if all devices have been CDP scanned.
    all_devices_cdp_scanned = False

    while(all_devices_cdp_scanned) == False:
        # Locate all CDP neighbors and add their information to the data dictionary, starting at the source device.
        # Loop through each neighbor til all neighbors are discovered.

        # Check if the current device have already been scanned.
        for key, value in list(devices.items()):
            print("Now scanning " + value["hostname"])
            if value["cdp_scanned"]:
                print("This device have already been scanned.. Skipping..")
                continue

            n_conn = netmiko_conn(value["mgmt_ip"])
            cdp_neighbors = n_conn.send_command("show cdp neighbor detail", use_textfsm=True)

            # Loop through the discovered neighbors.
            for cdp_neighbor in cdp_neighbors:
                # Check if the discovered neighbor is already known.
                if cdp_neighbor["management_ip"] in devices.keys():
                    print("The discovered neighbor (" + cdp_neighbor["destination_host"] + ") already exists.. Skipping..")
                    continue

                # If the discovered neighbor is unknown add it to the devices dictionary.
                new_device = {
                    cdp_neighbor["management_ip"]:
                        {
                            "hostname": cdp_neighbor["destination_host"],
                            "mgmt_ip": cdp_neighbor["management_ip"],
                            "type": "cisco_ios",
                            "cdp_scanned": False
                        }
                    }

                # Update the devices dictionary with the new device.
                devices.update(new_device)

            # set the current device to cdp_scanned = True.
            value["cdp_scanned"] = True

        # Check if there are any un-scanned devices.
        scanned_counter = 0
        for key, value in devices.items():
            if value["cdp_scanned"] == False:
                scanned_counter += 1
        if scanned_counter == 0:
            print("All devices have been scanned..")
            all_devices_cdp_scanned = True

    return devices


# def gather_information(devices):
def gather_information():
    """
    :param devices: Expects a json variable containing network devices.
    :return: Returns a json variable containing devices and link information.


    """

    devices = {
        '192.168.187.201': {
            'cdp_scanned': True,
            'hostname': 'R1.lab',
            'mgmt_ip': '192.168.187.201',
            'type': 'cisco_ios'
        },
        '192.168.187.202': {
            'cdp_scanned': True,
            'hostname': 'R2.lab',
            'mgmt_ip': '192.168.187.202',
            'type': 'cisco_ios'
        },
        '192.168.187.203': {
            'cdp_scanned': True,
            'hostname': 'R3.lab',
            'mgmt_ip': '192.168.187.203',
            'type': 'cisco_ios'
        },
        '192.168.187.204': {
            'cdp_scanned': True,
            'hostname': 'R4.lab',
            'mgmt_ip': '192.168.187.204',
            'type': 'cisco_ios'
        }
    }

    for key, value in list(devices.items()):
        # print(value["hostname"])

        n_conn = netmiko_conn(value["mgmt_ip"])
        cdp_neighbors = n_conn.send_command("show cdp neighbor", use_textfsm=True)

        link_information_list = []

        # Locate all CDP enabled interfaces where a neighbor is known. Save the neighbor, local port and remote port.
        for cdp_neighbor in cdp_neighbors:
            cdp_link_information = {
                    cdp_neighbor["neighbor"]:
                        {
                            "neighbor": cdp_neighbor["neighbor"],
                            "local_interface": cdp_neighbor["local_interface"],
                            "remote_interface": cdp_neighbor["neighbor_interface"]
                        }
                    }
            link_information_list.append(cdp_link_information)

            # pprint(value["mgmt_ip"])
            value["mgmt_ip"] = {"cdp_link_information": link_information_list}

    pprint(devices)


def main():
    #devices = discover_devices()
    # pprint(devices)

    # data = gather_information(devices)
    data = gather_information()
    pprint(data)


if __name__ == "__main__":
    main()
