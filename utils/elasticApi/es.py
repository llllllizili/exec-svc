#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   es.py
@Time    :   2020/05/29 16:43:31
'''

import sys
import logging
from utils.jklog import jklog
from redis import ConnectionPool, Redis
from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, RequestError, NotFoundError, ConflictError
import datetime
# from django.db import transaction
import time

logger = logging.getLogger('console')


class ElasticHandle(object):

    def __init__(self):
        try:
            self.es = Elasticsearch(
                settings.ELASTIC_SEARCH.get('hosts')
                # sniff_on_start=True,
                # sniff_on_connection_fail=True,
            )

        except Exception as e:
            logger.error(repr(e))
            raise ConnectionError(repr(e))

    def es_health(self):
        try:
            self.es.cluster.health()
            return True
        except Exception as e:
            logger.error(repr(e))
            return False



    def generate_signal(self, job_num, status='PENDING', log=None, operator=None, result=None):
        """

        :param job_num:
        :param status:
        :param log:
        :param operator:
        :param result:
        :return:
        """
        if not self.es.indices.exists(settings.ELASTIC_SEARCH_INDEX_NAME):
            self.es.indices.create(
                index=settings.ELASTIC_SEARCH_INDEX_NAME,
                body=settings.ELASTIC_SEARCH_INDEX_MAP
                )

        data = {
            'job_num': job_num,
            'status': status,
            'create_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if log:
            data['logs'] = log

        if operator:
            data['operator'] = operator

        if result:
            data['result'] = result


        try:
            self.es.index(
                index=settings.ELASTIC_SEARCH_INDEX_NAME,
                doc_type='_doc',
                body=data,
                id=job_num
            )

            logger.debug('es: generate_signal {} success'.format(job_num))
            return True
        except RequestError as e:
            logger.error(repr(e))
            return False

    def update_field(self, job_num, field, value):
        """

        :param job_num:
        :param field:
        :param value:
        :return:
        """
        try:
            # data = self.es.get_source(index=ELASTIC_SEARCH_INDEX_NAME, id=job_num)

            update_data = {
                'doc': {
                    field: value
                }
            }
            self.es.update(index=settings.ELASTIC_SEARCH_INDEX_NAME, doc_type='_doc', id=job_num, body=update_data)

            logger.debug('update_field {} success'.format(job_num))

        except NotFoundError as e:
            logger.error(repr(e))
            return False
        except RequestError as e:
            logger.error(repr(e))
            return False

    def update_signal(self, job_num, status, log=None, result=None):
        """

        :param job_num:
        :param status:
        :param log:
        :param result:
        :return:
        """
        try:
            data = self.es.get_source(index=settings.ELASTIC_SEARCH_INDEX_NAME, id=job_num)

            if data:
                data['status'] = status

                logs = data.get('logs')
                res = data.get('result')

                if not res:
                    data['result'] = result
                else:
                    if not isinstance(res, list) or not isinstance(res, dict):
                        data['result'] = result

                if not logs:
                    data['logs'] = log + '\n'
                else:
                    data['logs'] = '{}{}\n'.format(logs, log)

                update_data = {'doc': data}

                self.es.update(
                    index=settings.ELASTIC_SEARCH_INDEX_NAME,
                    doc_type='_doc',
                    id=job_num,
                    body=update_data
                )

                logger.debug('update_signal {} success'.format(job_num))


        except NotFoundError as e:
            logger.error(repr(e))

            return False
        except RequestError as e:
            logger.error(repr(e))
            return False

    def send_log(self, job_num, log):
        """

        :param job_num:
        :param log:
        :return:
        """

        try:
            data = self.es.get_source(index=settings.ELASTIC_SEARCH_INDEX_NAME, id=job_num)

            logs = '{}{}\n'.format(data.get('logs'), log)
            update_data = {
                'doc': {'logs': logs}
            }
            self.es.update(index=settings.ELASTIC_SEARCH_INDEX_NAME, doc_type='_doc', id=job_num, body=update_data)
            
            logger.debug('send_log {} success'.format(job_num))

        except NotFoundError as e:
            logger.error(repr(e))
            return False
        except RequestError as e:
            logger.error(repr(e))
            return False

    def send_result(self, job_num, result, log):
        """

        :param result:
        :param job_num:
        :param log:
        :return:
        """
        try:

            num = 0

            while num < 100:
                version = self.es.get(
                    index=settings.ELASTIC_SEARCH_INDEX_NAME,
                    id=job_num
                ).get('_version')

                data = self.es.get_source(
                    index=settings.ELASTIC_SEARCH_INDEX_NAME,
                    id=job_num
                )

                if data:
                    logs = data.get('logs')
                    res = data.get('response')

                    if not res:
                        data['response'] = [result]
                    else:
                        if isinstance(res, list):
                            # res.append(result)
                            data['response'].append(result)

                    if not logs:
                        data['logs'] = log + '\n'
                    else:
                        data['logs'] = '{}{}\n'.format(logs, log)

                    response = self.es.index(
                        index=settings.ELASTIC_SEARCH_INDEX_NAME,
                        doc_type='_doc',
                        id=job_num,
                        body=data,
                        version=version + 1,
                        version_type='external',
                        ignore=[409]
                    )

                    if not response.get('error'):
                        break
                    elif response.get('error') and response.get('status') != 409:
                        break
                    
                    logger.debug('send_result {} success'.format(job_num))

                num += 1
                time.sleep(1)

        except NotFoundError as e:
            logger.error(repr(e))
            pass

        except RequestError as e:
            logger.error(repr(e))
            pass

        except ConflictError as e:
            logger.error(repr(e))
            pass

        except Exception as e:
            logger.error(repr(e))
            pass

    def _get_response(self,job_num):
        
        # self.es.indices.refresh(index=settings.ELASTIC_SEARCH_INDEX_NAME)

        try:
            num = 0

            while num < 6:

                data = self.es.get_source(
                    index=settings.ELASTIC_SEARCH_INDEX_NAME,
                    id=job_num
                )

                res = ''

                if data:
                    res = data.get('response')
                    if res:
                        break
                num += 2
                time.sleep(2)
            if not res:
                logger.error('_get_response is null (The log(result) may be on the way)')
                return False
            else:
                logger.debug(data)
                return True
        except NotFoundError as e:
            logger.error('{} - _get_response'.format(repr(e)))
            return False

        except RequestError as e:
            logger.error('{} - _get_response'.format(repr(e)))
            return False

        except ConflictError as e:
            logger.error('{} - _get_response'.format(repr(e)))
            return False

        except Exception as e:
            logger.error('{} - _get_response'.format(repr(e)))
            return False

    def __del__(self):
        if self.es:
            self.es.transport.close()


def get_status(job_num):
    """

    :param job_num:
    :return:
    """
    try:
        es = Elasticsearch(
            hosts=[{
                'host': settings.ELASTIC_SEARCH.get('host'),
                'port': settings.ELASTIC_SEARCH.get('port')
            }],
            sniff_on_start=True,
            sniff_on_connection_fail=True,
        )

        _source = es.get_source(index=settings.ELASTIC_SEARCH_INDEX_NAME, id=job_num)

        logger.debug('get_status {} success'.format(job_num))


        if _source.get('status'):
            logger.debug('get_status {} success'.format(job_num))
            return True, _source.get('status')
        logger.error('get_status {} failed'.format(job_num))
        return False, 'NO_STATUS'

    except ConnectionError as e:
        logger.error(repr(e))
        return False, 'NO_STATUS'

# def send_logs(job_num, log):
#     """
#
#     :param job_num:
#     :param log:
#     :return:
#     """
#     try:
#         es = Elasticsearch(hosts=[{'host': ELASTIC_SEARCH.get('host'), 'port': ELASTIC_SEARCH.get('port')}])
#
#         if not es.indices.exists(ELASTIC_SEARCH_INDEX_NAME):
#             es.indices.create(index=ELASTIC_SEARCH_INDEX_NAME, body=ELASTIC_SEARCH_INDEX_MAP)
#
#         data = {
#             'job_num': job_num,
#             'createDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#             'log': log
#         }
#
#         es.index(index=ELASTIC_SEARCH_INDEX_NAME, body=data)
#
#     except ConnectionError as e:
#         print(e)
#
#     except ElasticsearchException as e:
#         print(e)


