#!/usr/bin/env python3
"""
##########################
# test_netconf_query_6.py
##########################

Retrieve AXOS runniung via netconf.

"""
import logging
import json
import xml.dom.minidom
import xmltodict
from logging.config import dictConfig
from collections import defaultdict
import json
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString
from ncclient import manager
from ncclient.xml_ import to_ele
from pprint import pprint as pp
from getpass import getpass as gp


###############################################################################
# START INPUT VARIABLES
###############################################################################
DEVICE_DICT = {
    'host': input('Enter target E9 hostname or ipaddr: '),
    'user': input('Enter netconf_ssh login username: '),
    'password': gp('Enter netconf_ssh login password: '),
    'port': int(input('Enter netconf_ssh port [hit return for port 830]: ') or "830")
}
###############################################################################
# END INPUT VARIABLES
###############################################################################


###############################################################################
# VARIABLES 
###############################################################################
RPC_GET_CONFIG = """
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="100">
 <get-config>
  <source>
   <running/>
  </source>
 </get-config>
</rpc>
]]>]]>
"""


###############################################################################
# FUNCTION [0] TO SETUP LOGGING
###############################################################################
def init_logger():
    """
    DEFINE LOGGER FUNCTIONS
    """
    logging_config = dict(
        version=1,
        formatters={
            "format_f": {
                "format": "%(asctime)s %(name)-10s %(levelname)-6s %(message)s"
            }
        },
        handlers={
            "handler_h": {
                "class": "logging.StreamHandler",
                "formatter": "format_f",
                "level": logging.INFO,
            }
        },
        root={
            "handlers": ["handler_h"],
            "level": logging.DEBUG,
        },
    )
    dictConfig(logging_config)
    logger = logging.getLogger()
    logging.getLogger("netmiko").setLevel(logging.WARNING)
    if logger:
        return True


###############################################################################
# FUNCTION [1]
###############################################################################
def netconf_connect(net_info):
    """
    Est. Netconf via SSH connection to target. The external ncclient library
    is used for creating this connection.
    ----------------
    Expecting a dict
    """
    axos_conn = manager.connect(host=net_info['host'],
                                    username=net_info['user'],
                                    password=net_info['password'],
                                    port=net_info['port'],
                                    hostkey_verify=False,
                                    allow_agent=False,
                                    look_for_keys=False,
                                    timeout = 120)
    if axos_conn.connected:
        logging.info('{0} connected'.format(net_info['host']))
        return axos_conn
    else:
        return False


###############################################################################
# FUNCTION [2]
###############################################################################
def parse_xml(file_name):
    """
    Use etreee to parse
    """
    events = ("start", "end")
    context = ET.iterparse(file_name, events=events)
    #########################
    # CALL FUNCTION 3
    #########################
    return parse_2_trans(context)


###############################################################################
# FUNCTION [3]
###############################################################################
def parse_2_trans(context, cur_elem=None):
    """
    JSON Conversion
    """
    items = defaultdict(list)
    if cur_elem:
        items.update(cur_elem.attrib)
    text = ""
    for action, elem in context:
        if action == "start":
            items[elem.tag].append(parse_2_trans(context, elem))
        elif action == "end":
            text = elem.text.strip() if elem.text else ""
            elem.clear()
            break

    if len(items) == 0:
        return text

    return { k: v[0] if len(v) == 1 else v for k, v in items.items() }


###############################################################################
# MAIN
###############################################################################
def main():
    """
    MAIN
    """
    # Call the logger
    rpc_reply = ''
    file_zer0 = '/tmp/config.xml'
    file_one1 = '/tmp/config.json'
    start_logging = init_logger()
    if start_logging:
        logging.info("Ncclient script is starting.")
    with netconf_connect(DEVICE_DICT) as axos_query:
        logging.info('Targetting netconf host {0}'.format(DEVICE_DICT['host']))
        #logging.info('Calling rpc: {0}'.format(RPC_GET_CONFIG))
        try:
            rpc_reply = str(axos_query.get_config(source="running"))
            #
            if rpc_reply:
                logging.info("RPC/netconf got a reply")
                logging.info("Writing xml & json to file")
                with open((file_zer0), "w", encoding='UTF-8') as f_0:
                    f_0.write(str(rpc_reply))
                    f_0.close()
                json_data = parse_xml(file_zer0)
                with open((file_one1), "w", encoding='UTF-8') as f_1:
                    file_3 = json.dumps(json_data, indent=2)
                    f_1.write(file_3)
                    f_1.close()
        except Exception as sessionException:
            print("An exception occurred while closing the session :" + str(sessionException))


if __name__ == '__main__':
    main()
