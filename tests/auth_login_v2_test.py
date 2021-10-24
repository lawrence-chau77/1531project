import pytest
import requests

from src import config
from src.error import InputError

def test_auth_login_v1():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    register_auth_user_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()

    auth_login_input = {
        'email':'valid@gmail.com',
        'password':'password'
    }

    login_auth_user_id = requests.post(config.url + 'auth/login/v2', json=auth_login_input)

    assert login_auth_user_id.status_code == 200
    assert register_auth_user_id['auth_user_id'] == login_auth_user_id.json()['auth_user_id']
    assert register_auth_user_id['token'] != login_auth_user_id.json()['token']

def test_unregistered_email():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()

    auth_login_input = {
        'email':'unregistered@gmail.com',
        'password':'password'
    }

    login_return = requests.post(config.url + 'auth/login/v2', json=auth_login_input)

    assert login_return.status_code == InputError.code
    
def test_incorrect_password():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    auth_login_input = {
        'email':'valid@gmail.com',
        'password':'notpassword'
    }

    login_return = requests.post(config.url + 'auth/login/v2', json=auth_login_input)

    assert login_return.status_code == InputError.code
