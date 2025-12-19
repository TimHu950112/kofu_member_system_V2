from flask import request, session, render_template, make_response, redirect, flash
from flask_restful import Resource
from functools import wraps
from datetime import datetime, timedelta
import pytz

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            # flash('請先登入')
            return redirect('/index')
        return f(*args, **kwargs)
    return decorated_function

class CustomerResource(Resource):
    def __init__(self, **kwargs):
        self.customer = kwargs['customer']

    @login_required
    def get(self):
        data = request.args.get('phone')
        phone = data
        result = []
        for i in self.customer.find({'phone':{'$regex':phone}}):
            result.append({'phone':i['phone'],'name':i['name'],'permanent_status':i['permanent_status'],'active_year':i['active_year']})
        return result, 200

    @login_required
    def post(self):
        data = request.get_json()
        name = data.get('name')
        phone = data.get('phone')
        permanent_status = data.get('permanent_status')
        result = self.customer.find_one({'phone':phone})
        if result != None:
            self.customer.update_one({'phone':phone},{'$set':{'active_year':datetime.now(pytz.timezone("Asia/Taipei")).year,'permanent_status':permanent_status}})
            return {'message': 'updated'}, 200
        else:
            self.customer.insert_one({'name':name,'phone':phone,'permanent_status':permanent_status,'active_year':datetime.now(pytz.timezone("Asia/Taipei")).year})
            return {'message': 'added'}, 200
    

class CoffeeResource(Resource):
    def __init__(self, **kwargs):
        self.coffee = kwargs['coffee']

    @login_required
    def get(self):
        data = request.args.get('phone')
        phone = data
        result = []
        for i in self.coffee.find({'phone':{'$regex':phone}}):
            result.append({'phone':i['phone'],'left':i['left']})
        return result, 200


    @login_required
    def post(self):
        data = request.get_json()
        phone = data.get('phone')
        function = data.get('function')
        item = int(data.get('item'))
        number = int(data.get('number'))
        result = self.coffee.find_one({'phone':phone})
        if result != None and len(result)!=0:
            if function == 'add_coffee':
                self.coffee.update_one({'phone':phone},{'$set':{'left.'+str(item):result['left'][str(item)]+number}})
            elif function == 'take_away':
                self.coffee.update_one({'phone':phone},{'$set':{'left.'+str(item):result['left'][str(item)]-number}})
            else:
                return {'message':'function error'}, 400
            return {'message':'updated'}, 200
        else:
            if function == 'add_coffee':
                if item == 70:
                    self.coffee.insert_one({'phone':phone,'left':{str(item):number,'80':0}})
                elif item == 80:
                    self.coffee.insert_one({'phone':phone,'left':{'70':0,str(item):number}})
                else:
                    return {'message':'item error'}, 400
                return {'message':'added'}, 200
            else:
                return {'message':'function error'}, 400
# 資料庫架構
# {
#     'phone':'',
#     'coffee_list':{'item1':0,'item2':},
#     'line_id':'',
#     'log':[
#         {
#             'time':'',
#             'coffee_list':['item1':0,'item2':0]
#         }
#     ]
# }

class CustomerSelfCheckResource(Resource):
    def __init__(self, **kwargs):
        self.customer = kwargs['customer']

    def get(self):
        phone = request.args.get('phone')
        if not phone:
            return {'customers': []}, 200

        result = []
        # 使用精確匹配而非模糊搜尋
        customer = self.customer.find_one({'phone': phone})
        if customer:
            result.append({
                'phone': customer['phone'],
                'name': customer['name'],
                'permanent_status': customer['permanent_status'],
                'active_year': customer['active_year']
            })
        return {'customers': result}, 200

class CoffeeLogResource(Resource):
    def __init__(self, **kwargs):
        self.coffee_log = kwargs['coffee_log']

    def get(self):
            # 當前時間（台北時區）
            tz = pytz.timezone("Asia/Taipei")
            now_tz = datetime.now(tz)
            one_week_ago_tz = now_tz - timedelta(days=7)

            # 轉換為 UTC 時間
            now_utc = now_tz.astimezone(pytz.utc)
            one_week_ago_utc = one_week_ago_tz.astimezone(pytz.utc)

            # 查詢 log_time 在範圍內的紀錄
            logs = self.coffee_log.find({
                'log_time': {
                    '$gte': one_week_ago_utc,
                    '$lt': now_utc
                }
            })

            # 將查詢結果轉為列表並處理 ObjectId
            result = []
            for log in logs:
                log['_id'] = str(log['_id'])  # 將 ObjectId 轉換為字串
                log['log_time'] = str(log['log_time'])  # 將時間轉換為字串
                result.append(log)
                result.reverse()
            return result, 200