# -*- coding: utf-8 -*-

""" Implement the cmd3 command.
    COPY模式：将外部系统数据同步到科研系统
"""

import logging
import json
from datetime import date, datetime

from flask import Flask, Response, request, jsonify
from flask.views import MethodView

from ..core import config
from .resource import get_redis_connection, get_mysql_connection, get_oracle_connection

logger = logging.getLogger(__name__)


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
    logger.debug("executing cmd2 command with %s", name)
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
        table_config.get('condition') if table_config.get(
            'condition') else '1=1'
    )
    logger.info('Executing %s', sql)

    temp_target = '{}:tmp'.format(target)
    redis_conn = get_redis_connection()
    try:
        if table_config.get('source') == 'mysql':
            connection = get_mysql_connection()
        else:
            connection = get_oracle_connection()

        redis_conn.delete(temp_target)

        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            new_row = dict()
            new_key = target
            for _origin, _new in table_config.get('fields').items():
                origin_value = row.get(_origin)
                if isinstance(origin_value, str):
                    origin_value = origin_value.strip()

                # 字段值映射判断
                map_rule = rule_config.get(_origin) if rule_config else None
                map_value = map_rule.get(origin_value) if map_rule else None
                new_row[_new] = map_value if map_value else origin_value

                if _origin in table_config.get('pk'):
                    new_key = '{}:{}'.format(new_key, new_row.get(_new))

            redis_conn.hmset(new_key, new_row)

            v = json.dumps(new_row, ensure_ascii=False)
            redis_conn.sadd(temp_target, v)

        redis_conn.rename(temp_target, target)
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
