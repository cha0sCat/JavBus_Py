# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
from datetime import datetime
import json
import requests
import pymongo
import pymysql
from scrapy.utils.project import get_project_settings
settings = get_project_settings()

from JavBus.items import MainItem, StarItem


class DataStorePipeline(object):
    def __init__(self):
        self.MainItem_cloud_functions_url = settings["MAINITEM_CF_URL"]
        self.StarItem_cloud_functions_url = settings["STARITEM_CF_URL"]

    def process_item(self, item, spider):
        if isinstance(item, MainItem):
            requests.post(self.MainItem_cloud_functions_url, data={"data": json.dumps(dict(item), ensure_ascii=False)})
        elif isinstance(item, StarItem):
            requests.post(self.StarItem_cloud_functions_url, data={"data": json.dumps(dict(item), ensure_ascii=False)})
        return item


class JsonPipeline(object):
    def __init__(self):
        self.main_file = codecs.open('JavBus.json', 'w', encoding='utf-8')
        self.star_file = codecs.open('JavBus_Star.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        # 根据Item的类型保存到不同的文件
        if isinstance(item, MainItem):
            self.main_file.write(line)
        elif isinstance(item, StarItem):
            self.star_file.write(line)
        return item

    def spider_closed(self, spider):
        self.main_file.close()
        self.star_file.close()


class MysqlPipeline(object):
    """
    Mysql保存
    """

    def __init__(self):
        self.conn = pymysql.connect(host=settings['MYSQL_HOST'], user=settings['MYSQL_USER'],
                                    password=settings['MYSQL_PASSWORD'], port=settings['MYSQL_PORT'],
                                    db=settings['MYSQL_DB'])
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            post_item = dict(item)  # 把item转化成字典形式
            if isinstance(item, MainItem):
                # 将MainItem拆分放入多个库
                magnets = post_item['magnets']
                for x in magnets:
                    x['movie_code'] = post_item['code']
                    self.insert_data('magnet', x)
                previews = post_item['previews']
                for x in previews:
                    preview = {
                        'movie_code': post_item['code'],
                        'preview': x
                    }
                    self.insert_data('preview', preview)

                stars = post_item['stars']
                for x in stars:
                    x.pop('name')
                    x['star_code'] = x['code']
                    x.pop('code')
                    x['movie_code'] = post_item['code']
                    self.insert_data('movie_star', x)
                tags = post_item['tags']
                for x in tags:
                    x['censored'] = post_item['censored']
                    self.insert_data('tag', x)
                    self.insert_data('movie_tag', {'movie_code': post_item['code'], 'tag_code': x['code']})
                studio = post_item['studio']
                label = post_item['label']
                director = post_item['director']
                series = post_item['series']
                if studio:
                    self.insert_data('studio', studio)
                    self.insert_data('movie_studio', {'movie_code': post_item['code'], 'studio_code': studio['code']})
                    post_item['studio'] = post_item['studio']['name']
                else:
                    post_item['studio'] = ''
                if label:
                    # self.coll_label.insert(label)
                    self.insert_data('label', label)
                    self.insert_data('movie_label', {'movie_code': post_item['code'], 'label_code': studio['code']})
                    post_item['label'] = post_item['label']['name']
                else:
                    post_item['label'] = ''
                if director:
                    self.insert_data('director', director)
                    self.insert_data('movie_director',
                                     {'movie_code': post_item['code'], 'director_code': studio['code']})
                    post_item['director'] = post_item['director']['name']
                else:
                    post_item['director'] = ''
                if series:
                    self.insert_data('series', series)
                    self.insert_data('movie_series', {'movie_code': post_item['code'], 'series_code': studio['code']})
                    post_item['series'] = post_item['series']['name']
                else:
                    post_item['series'] = ''

                post_item.pop('previews')
                post_item.pop('magnets')
                post_item.pop('tags')
                post_item.pop('stars')
                self.insert_data('movie', post_item)
            elif isinstance(item, StarItem):
                self.insert_data('star', post_item)
            self.conn.commit()
        except:
            self.conn.rollback()
        # return item  # 会在控制台输出原item数据，可以选择不写

    def spider_closed(self, spider):
        print('Failed')
        self.cursor.close()
        self.conn.close()

    def insert_data(self, table, data):
        """
        通用插入方法
        :param data:数据
        :param table: 表明
        :return:
        """
        data['updatetime'] = datetime.now()
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE'.format(table=table, keys=keys,
                                                                                             values=values)
        update = ','.join([" {key} = %s".format(key=key) for key in data])
        sql += update
        print(sql)
        self.cursor.execute(sql, tuple(data.values()) * 2)


class MongoPipeline(object):
    def __init__(self):
        # 链接数据库
        self.client = pymongo.MongoClient(settings['MONGO_URI'])
        # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        self.db = self.client[settings['MONGO_DB']]  # 获得数据库的句柄
        self.coll_movie = self.db[settings['MONGO_COLL_MOVIE']]  # 获得movie_collection的句柄
        self.coll_star = self.db[settings['MONGO_COLL_STAR']]  # 获得star_collection的句柄

    def process_item(self, item, spider):
        postItem = dict(item)  # 把item转化成字典形式
        if isinstance(item, MainItem):
            self.coll_movie.insert(postItem)  # 向数据库插入一条记录

        elif isinstance(item, StarItem):
            self.coll_star.insert(postItem)  # 向数据库插入一条记录
        return item  # 会在控制台输出原item数据，可以选择不写
