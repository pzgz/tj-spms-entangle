# -*- coding: utf-8 -*-

""" Implement the cmd3 command.

"""

import logging
from datetime import date, datetime
import threading
from pprint import pprint

from flask import Flask, Response, request, jsonify
from flask.views import  MethodView

from ..core import config
from .resource import get_redis_connection, get_mysql_connection, get_oracle_connection

logger = logging.getLogger(__name__)

exit_flag = 0


class MyResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (list, dict)):
            response = jsonify(response)
        return super().force_type(response, environ)


class FinanceAPI(MethodView):
    def get(self):
        option = request.args.get('option')
        if option == 'list1':
            return self.test_list()

        msg = {
            'info': '`option` is needed in url as a url parameter',
            'avilable option values': 'list1, list2, test_dict1, test_dict2, test_dict2'
        }
        return msg

    def post(self):
        pass

    def test_list(self):
        data = [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}]
        return data


app = Flask(__name__)
app.response_class = MyResponse
app.add_url_rule('/codes/', view_func=FinanceAPI.as_view('codes'))

def main(name="World", year=None, history=False):
    """ Execute the command.    
    """
    logger.debug("executing cmd3 command with %s", name)
    table_config = config.entangle.get(name)
    if not table_config:
        logger.error('%s is not exist.', name)
        return
    else:
        logger.debug(table_config)

    current_year = datetime.now().year
    if history:
        start_year = table_config.get('history')
        if start_year:
            for year in range(start_year, current_year):
                _duplicate(name+str(year), table_config, year)
    else:
        _duplicate(name, table_config)
    # app.debug = True
    # app.run(host='0.0.0.0', port=5000)


def _duplicate(table_name, table_config, year=None):
    if year:
        target = table_config.get('target').format(year=year)
    else:
        target = table_config.get('target')

    rule_config = table_config.get('rules')

    sql = 'SELECT {} FROM {} WHERE {}'.format(
        ','.join(table_config.get('fields').keys()),
        table_name,
        table_config.get('condition') if table_config.get('condition') else '1=1'
    )
    logger.info('Executing %s', sql)

    redis_conn = get_redis_connection()
    try:
        if table_config.get('source') == 'mysql':
            connection = get_mysql_connection()
        else:
            connection = get_oracle_connection()

        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            new_row = dict()

            for _origin, _new in table_config.get('fields').items():
                origin_value = row.get(_origin)
                if isinstance(origin_value, str):
                    origin_value = origin_value.strip()

                # 字段值映射判断
                map_rule = rule_config.get(_origin) if rule_config else None
                map_value = map_rule.get(origin_value) if map_rule else None
                new_row[_new] = map_value if map_value else origin_value
                
            redis_conn.sadd(target, new_row)
    except:
        logger.exception('Error: unable to fetch data')
    finally:
        cursor.close()
        connection.close()


@app.route('/')
def root():
    t = {
        'a': 1,
        'b': 2,
        'c': [3, 4, 5]
    }
    return jsonify(t)


@app.route('/hello')
def hello():
    sql = "select BCODE,BNAME from PS_ETL_CW_BUDSTR where tcode='AA27' and SUBSTR(bcode,1,8)='AA270201' and LENGTH(trim(bcode))>8 order by bcode"

    new_rows = list()

    try:
        connection = get_oracle_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            new_row = dict()
            for k, v in row.items():
                new_row[k] = v.strip() if isinstance(v, str) else v

            new_rows.append(new_row)
    except:
        logger.exception('Error: unable to fetch data')
    finally:
        cursor.close()
        connection.close()

    return new_rows


def handleRedisQueue():
    handler = FinanceHandler(1, 'spms:abc')
    handler.start()
    handler.join()

class FinanceHandler(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        logger.info('Starting listener %s...', self.name)
        conn = get_redis_connection()
        while not exit_flag:
            result = conn.brpop(self.name, 30)
            pprint(result)

        logger.info('Exit listener %s.', self.name)


