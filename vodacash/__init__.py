from datetime import datetime
from time import sleep
import requests
import json
from lxml import etree

C2BCallbackResponse = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<response>
<dataItem>
<name>ResponseCode<</name>
<type>String</type>
<value>200</value>
</dataItem>
</response>
"""
B2CCallbackResponse = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<response>
<dataItem>
<name>ResponseCode<</name>
<type>String</type>
<value>200</value>
</dataItem>
<dataItem>
<name>RESULT_CODE<</name>
<type>String</type>
<value>Received</value>
</dataItem>
</response>
"""


def strdate(dt):
    ax = str(dt)
    return ax.split('.')[0].replace('-', '').replace(' ', '').replace(':', '')


def parse_async_result(content):
    root = etree.from_string(content)
    js_out = {}
    keys = []
    for dataItem in root.xpath("//dataItem"):
        name, t, value = dataItem.getchildren()
        keys.append({name.text: value.text})
    [js_out.update(ks) for ks in keys]
    return js_out


class Vodacash(object):
    def __init__(self, username, password,  *args, **kwargs):
        self.LOGIN_URL = "http://167.71.65.114/api/v1/login"
        self.C2B_URL = "http://167.71.65.114/api/v1/c2b"
        self.C2B_CB_URL = "http://167.71.65.114/api/v1/c2b_callback"
        self.B2C_URL = "http://167.71.65.114/api/v1/b2c"
        self.B2C_CB_URL = "http://167.71.65.114/api/v1/b2c_callback"
        self.Username = username
        self.Password = password
        self.token = None
        self.shortcode = None
        self.serviceprovidercode = None
        self.callback_channel = 2
        self.authenticate()

    def authenticate(self):
        conn = requests.post(
            self.LOGIN_URL, json={"Username": self.Username, "Password": self.Password})
        result = json.loads(conn.content)
        self.token = result["token"]
        conn.connection.close()

    def c2b(self, customer_msisdn, amount,  *args, **kwargs):
        self.authenticate()
        result = requests.post(
            self.C2B_URL,
            json={
                "Amount": amount,
                "CustomerMSISDN": customer_msisdn,
                "Date": strdate(datetime.utcnow()),
                "thirdpartyref": 'R'+strdate(datetime.now()),
                "token": str(self.token),
                "callback_url": str(self.C2B_CB_URL),
            }
        ).content
        # print(result)
        result = json.loads(result)
        return result

    def b2c(self, customer_msisdn, amount,  *args, **kwargs):
        self.authenticate()
        result = requests.post(
            self.B2C_URL,
            json={
                "Amount": amount,
                "CustomerMSISDN": customer_msisdn,
                "Date": strdate(datetime.utcnow()),
                "thirdpartyref": 'R'+strdate(datetime.now()),
                "token": str(self.token),
                "callback_url": str(self.B2C_CB_URL),
            }
        ).content
        # print(result)
        result = json.loads(result)
        return result
