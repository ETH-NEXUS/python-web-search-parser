import socket
import requests.packages.urllib3.util.connection as urllib3_cn 


def allowed_gai_family():
    """ Force urllib3 to use ipv4 """
    family = socket.AF_INET
    return family


urllib3_cn.allowed_gai_family = allowed_gai_family
