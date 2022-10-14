import requests
from pyquery import PyQuery as pq
import math
import time,datetime
import connector
db =connector.mysql_conn()
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
headers = {
    'User-Agent':UA
}

def count_call(func):
    nums = [0, datetime.datetime.now()]
    def call_func(*args,**kwargs):
        nums[0] += 1
        res = func(*args,**kwargs)
        time1 = nums[1]
        time2 = datetime.datetime.now()
        time_diff = (time2 - time1).seconds
        if (time_diff > 10):
            print('\r',end='',flush=True)
            nums[1] = time2
            speed = nums[0] / time_diff
            nums[0] = 0
            # print('\r',end='')
            print('{}\t当前速率：{}条/s'.format(time2.strftime('%H:%M:%S'),speed*30),end="",flush=True)
        return res
    return call_func

@count_call
def get_response(condition=''):
    # time.sleep(1)
    url = 'https://hf.ke.com/ershoufang/'+condition
    response = requests.get(url,headers).text
    doc = pq(response)
    return doc

def gen_condition():
    city = [#'baohe','shushan','luyang','yaohai','zhengwu',
            'binhuxinqu','jingkai2',
            'gaoxin8','xinzhan','feidong','feixi','changfeng','lujiangxian']
    def mix_condition(x):
        range = ['bp0ep50','bp51ep100','bp101ep120','bp121ep150','bp151ep180',
             'bp181ep200','bp201ep220','bp221ep250','bp251ep300','bp301ep350','bp351ep1000']
        return [x+'/'+i+'/' for i in range]
    condition = map(mix_condition,city)
    return condition

def get_num(condition):
    res = get_response(condition)
    num = math.ceil(int(res('.resultDes span').text())/30)
    if num>100:print(condition)
    if num==0: return []
    return ['pg'+str(i)+condition for i in range(1,num)]

def move_condition(city_conditions):
    page_list = []
    for condition in city_conditions:
        pages = get_num(condition)
        if pages == []: return page_list
        page_list += pages
    return page_list


def db_insert(fields,data_list):
    db.insert_many('beike', fields, data_list)

def resolve_res(city,page_list):
    fields = ['area', 'id', 'address', 'floor', 'build_time', 'house_type', 'square_meters', 'toward', 'total_price',
              'unit_price']
    data_list = []
    while page_list:
        page = page_list.pop(0)
        res = get_response(page)
        items = res('.sellListContent .address').items()
        floor,build_time,house_type,square_meters,toward='','','','',''
        for item in items:
            id = item('.priceInfo>.unitPrice').attr('data-hid')
            address = item('.positionInfo>a').text()
            house_info = item('.houseInfo').text().split(' | ')
            for house_item in house_info:
                if '楼层' in house_item:
                    floor = house_item
                elif '年建' in house_item:
                    build_time = house_item
                elif '厅' in house_item:
                    house_type = house_item
                elif '平米' in house_item:
                    square_meters = house_item
                elif '东' in house_item or '南' in house_item or '西' in house_item or '北' in house_item:
                    toward = house_item
            total_price = float(item('.priceInfo>.totalPrice').text().replace('万',''))*10000
            unit_price = float(item('.priceInfo>.unitPrice').text().replace('元/平','').replace(',',''))
            data = (city,id,address,floor,build_time,house_type,square_meters,toward,total_price,unit_price)
            data_list.append(data)
    db_insert(fields,data_list)


def main():
    conditions = gen_condition()
    for city_conditions in conditions:
        page_list = move_condition(city_conditions)
        city = city_conditions[0].split('/')[0]
        print('\n'+'-'*10+city+'-'*10)
        resolve_res(city,page_list)

main()