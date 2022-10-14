import pymysql
import datetime

class mysql_conn():

    def __init__(self):
        self.conn = pymysql.connect(
            host='***',
            port=3306,
            user='root',
            passwd='***',
            database='spider',
            charset='utf8'
        )

        self.cursor = self.conn.cursor()

    def insert_many(self,table,fields,data):
        print('\n数据写入开始'+'-'*10)
        time1 = datetime.datetime.now()
        sql = 'insert into {}({}) values({});'.format(table,','.join(fields),','.join(['%s' for i in range(len(data[0]))]))
        num = len(data)
        self.cursor.executemany(sql,data)
        self.conn.commit()
        time2 = datetime.datetime.now()
        time3 = (time2-time1).seconds
        time3 = 1 if time3==0 else time3

        speed = num/time3
        print('写入速度为：{}条/秒'.format(speed))

# db = mysql_conn()
# fields = ['area','id','address','floor','build_time','house_type','square_meters','toward','total_price','unit_price']
# data = ['1','1','1','1','1','1','1','1','1','1']
# db.insert('beike',fields,data)
