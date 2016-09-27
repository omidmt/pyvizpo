from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import requests
import json
import logging

class VizPortalApi(object):

    gen_public_key_api = 'vizportal/api/web/v1/generatePublicKey'
    gen_pub_key_method = 'generatePublicKey'

    login_api = 'vizportal/api/web/v1/login'
    login_method = 'login'

    set_schedule_status_api = 'vizportal/api/web/v1/setEnabledStatusForSchedules'
    set_schedule_method = 'setEnabledStatusForSchedules'

    """VizPortalApi"""

    def __init__(self, ip, port, tableau_version=10):
        super(VizPortalApi, self).__init__()
        self.ip = ip
        self.port = port
        self.base_url = 'http://' + self.ip + ':' + str(self.port) + '/'
        logging.debug('Base url composed as {}'.format(self.base_url))
        self.cookies = {}

    def get_public_key(self):
        """return tuple as (keyId, {n, e})"""
        r = self.__send_request(self.gen_public_key_api, self.gen_pub_key_method, {})

        if r.status_code == 200:
            res = r.json()
            logging.debug('Got public key keyId: {} , key: {}'.format(res['result']['keyId'], res['result']['key']))
            return (res['result']['keyId'], res['result']['key'])
        else:
            logging.error('Getting public key request failed status code: {}'.format(r.status_code))
            (None, None)

    def login(self, username, password):
        kid, key = self.get_public_key()
        if kid and key:
            enc_password = self.__rsa_encrypt(password, key['n'], key['e'])
            logging.debug('Encrypting password')
        else:
            return None

        r = self.__send_request(self.login_api, self.login_method, {'username': username, 'encryptedPassword': enc_password, 'keyId': kid})
        logging.debug('login status code: {} result: {}'.format(r.status_code, r.content))
        result = r.json()
        if r.status_code == 200:
            logging.info('successful login')
            logging.debug(r.content)
            self.cookies = r.cookies
            self.x_token = r.cookies['XSRF-TOKEN']
            logging.debug('Session cookie: {} x-token: {}'.format(self.cookies, self.x_token))
        else:
            logging.info('login failed with status code: {} content: '.format(r.status_code, r.content))
            raise VizPortalError('Login failed')

    def logout(self):
        raise Exception('Not Implemented Yet')

    def disable_schedule(self, id):
        logging.info('Disable schedule id {}'.format(id))
        r = self.__send_request(self.set_schedule_status_api, self.set_schedule_method, {'enabled': False, 'ids': [id]})
        logging.debug('Disabling schedule status code: {} result: {}'.format(r.status_code, r.content))

    def enable_schedule(self, id):
        logging.info('Enable schedule id {}'.format(id))
        r = self.__send_request(self.set_schedule_status_api, self.set_schedule_method, {'enabled': True, 'ids': [id]})
        logging.debug('Enabling schedule status code: {} result: {}'.format(r.status_code, r.content))


    def __send_request(self, api, method, params):
        if self.cookies:
            logging.debug('Sending {} request with cookie and params {}'.format(method, params))
            return requests.post(self.base_url + api, data=json.dumps({'method': method, 'params': params}),
                                 cookies= self.cookies, headers={'X-XSRF-TOKEN': self.x_token})
        else:
            logging.debug('Sending {} request without cookie and params {}'.format(method, params))
            return requests.post(self.base_url + api, data=json.dumps({'method': method, 'params': params}))

    def __rsa_encrypt(self, text, n ,e):
        """Encrypt text with public key modulus and exponent with RSA PKCS1"""
        logging.debug('Encrypt with public key n: {} e: {}'.format(n, e))
        rsa = RSA.construct((long(n, 16), long(e, 16)))
        pkcs1 = PKCS1_v1_5.new(rsa)
        enc = pkcs1.encrypt(text)
        return enc.encode('hex')

class VizPortalError(Exception):

    def __init__(self, msg):
         self.message = msg

    def __str__(self):
         return repr(self.message)

