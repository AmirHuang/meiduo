# _*_ coding: utf-8 _*_
# @Time     : 10:51
# @Author   : Amir
# @Site     : 
# @File     : hyt_message.py
# @Software : PyCharm

import requests
import json


class Hyt_Message(object):

    def __init__(self):
        self.send_url = 'http://dc.sun-hyt.com/interface/seedmsg'

    def send_message(self, code, mobile):
        # 需要传递的参数
        params = {
            'msg': code,
            'devcode': 'Amir',
            'phone': mobile
        }
        response = requests.post(self.send_url, data=params)
        re_dict = json.loads(response.text)
        print(re_dict)
        return re_dict


if __name__ == '__main__':
    hyt_message = Hyt_Message()
    hyt_message.send_message(123, 15766205544)

