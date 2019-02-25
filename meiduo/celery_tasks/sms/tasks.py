from utils.hyt_message import Hyt_Message
from celery_tasks.main import app


# 发送对象的方法
@app.task(name="send_sms_code")
def send_sms_code(sms_code, mobile):
    ccp = Hyt_Message()
    return ccp.send_message(sms_code, mobile)
