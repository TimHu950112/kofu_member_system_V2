from resources.qrcode_api import generate_qrcode
from datetime import datetime,timedelta
from PIL import Image, ImageDraw
import os,json

def load_template(name):
    template_path = os.path.join(os.path.dirname(__file__), name)
    with open(template_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_message_template(user_message):
    if user_message.lower() == "template":
        template = load_template("linebot_template.json")
        return json.dumps(template)
    elif user_message.lower() == "qrcode":
        template = load_template("linebot_bubble.json")
        template['body']['contents'][1]['contents'][0]['contents'][1]['text']='5分鐘 ('+(datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")+')'
        template['body']['contents'][1]['contents'][1]['contents'][1]['text']='品項幾杯'
        template['body']['contents'][1]['contents'][2]['contents'][1]['text']='編號'
        qrcode_link=generate_qrcode("https://youtube.com")
        template['body']['contents'][2]['contents'][0]['url']=qrcode_link[0]
        template['body']['contents'][2]['contents'][1]['action']['uri']=qrcode_link[1]
        return json.dumps(template)
    else:
        # 如果不是要求模板，回傳普通文字訊息
        return json.dumps({
            "type": "text",
            "text": f"你說了：{user_message}"
        }, indent=4)