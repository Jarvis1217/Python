# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql

class BilibiliPipeline:
    def process_item(self, item, spider):

        host = '127.0.0.1'
        user = 'root'
        psd = 'root'
        db = 'bilibili'
        c = 'utf8'
        port = 3306
        # 数据库连接
        con = pymysql.connect(host=host, user=user, passwd=psd, db=db, charset=c, port=port)
        # 数据库游标
        cue = con.cursor()
        print("mysql connect succes")
        # print(item['rank'],item['title'],item['url'],item['grade'],"在这里执行")

        try:
            cue.execute(
                """insert into video_videolist(rank,title,url,grade)
                               value (%s, %s, %s,%s)""",
                (item['rank'],
                 item['title'],
                 item['url'],
                 item['grade'],
                 ))

            print("Insert success")
        except Exception as e:
            print('Insert error:', e)
            con.rollback()
        else:
            con.commit()
        con.close()

        return item
