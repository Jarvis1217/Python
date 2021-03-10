# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql


class WymusicPipeline:
    def process_item(self, item, spider):

        host = '127.0.0.1'
        user = 'root'
        psd = 'root'
        db = 'music'
        c = 'utf8'
        port = 3306
        # 数据库连接
        con = pymysql.connect(host=host, user=user, passwd=psd, db=db, charset=c, port=port)
        # 数据库游标
        cue = con.cursor()
        print("mysql connect succes")

        url = "http://music.163.com/song/media/outer/url?id=" + str(item['music_id']) + ".mp3"
        # sql = '''
        # insert into msc_download_musiclist (playlist,Musicname,url) values(%s,%s,%s) %()
        # '''
        try:
            cue.execute(
                """insert into msc_download_musiclist(playlist,Musicname,url)
                               value (%s, %s, %s)""",
                (item['playlist_name'],
                 item['music_name'],
                 url
                 ))

            print("Insert success")
        except Exception as e:
            print('Insert error:', e)
            con.rollback()
        else:
            con.commit()
        con.close()

        return item
