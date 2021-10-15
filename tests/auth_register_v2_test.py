import pytest
import requests

from src import config
from src.auth import auth_register_v1, auth_login_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError

# Test if function works when given correct input
def test_auth_register_v1():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    register_auth_user_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['auth_user_id']

    auth_login_input = {
        'email':'valid@gmail.com',
        'password':'password'
    }

    login_auth_user_id = requests.post(config.url + 'auth/login/v2', json=auth_login_input).json()['auth_user_id']

    assert register_auth_user_id == login_auth_user_id

# Test if function is given an invalid email
def test_invalid_email():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'invalidemail',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    register_return = requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    assert register_return.status_code == InputError.code

# Test if function is given an email that has already been registered
def test_registered_email():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    requests.post(config.url + 'auth/register/v2', json=auth_register_input)
    
    register_return = requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    assert register_return.status_code == InputError.code

# Test if function is given a password < 6 chracters
def test_short_password():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'pass',
        'name_first':'First',
        'name_last':'Last'
    }

    register_return = requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    assert register_return.status_code == InputError.code

# Test if function is given a first name < 1 character
def test_short_firstname():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'',
        'name_last':'Last'
    }

    register_return = requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    assert register_return.status_code == InputError.code

# Test if function is given a first name > 50 characters
def test_long_firstname():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'name_last':'Last'
    }

    register_return = requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    assert register_return.status_code == InputError.code

# Test if function is given a last name < 1 character
def test_short_lastname():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':''
    }

    register_return = requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    assert register_return.status_code == InputError.code

# Test if function is given a last name > 50 characters
def test_long_lastname(): 
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    }

    register_return = requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    assert register_return.status_code == InputError.code

# Test if function is given a first name and last name that do not contain alphanumeric characters
def test_no_alphanumeric_characters():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'@#!$!',
        'name_last':'@$#!$*'
    }

    register_return = requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    assert register_return.status_code == InputError.code

# Test if function generates correct handle
def test_handle():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    channel_id = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name': 'name', 'is_public': True}).json()['channel_id']

    handle = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id}).json()['all_members'][0]['handle_str']

    assert handle == "firstlast"

# Test if function generates correct handle when given numeric first and last names
def test_handle_numeric():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'12345',
        'name_last':'12345'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    channel_id = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name': 'name', 'is_public': True}).json()['channel_id']

    handle = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id}).json()['all_members'][0]['handle_str']

    assert handle == "1234512345"

# Test if function generates correct handle when given uppercase first an last names
def test_handle_uppercase():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'FIRST',
        'name_last':'LAST'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    channel_id = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name': 'name', 'is_public': True}).json()['channel_id']

    handle = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id}).json()['all_members'][0]['handle_str']

    assert handle == "firstlast"

# Test if function generates correct handle when the same handle already exists
def test_double_handles():
    requests.delete(config.url + '/clear/v1')

    requests.post(config.url + 'auth/register/v2', params={'email': 'valid@gmail.com', 'password': 'password', 'name_first': 'First', 'name_last': 'Last'})

    auth_register_input = {
        'email':'other@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    channel_id = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name': 'name', 'is_public': True}).json()['channel_id']

    handle = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id}).json()['all_members'][0]['handle_str']

    assert handle == "firstlast0"

# Test if function generates correct handle if multiple of the same handle already exist
def test_multiple_handles():
    requests.delete(config.url + '/clear/v1')

    requests.post(config.url + 'auth/register/v2', params={'email': 'valid@gmail.com', 'password': 'password', 'name_first': 'First', 'name_last': 'Last'})
    requests.post(config.url + 'auth/register/v2', params={'email': 'other@gmail.com', 'password': 'password', 'name_first': 'First', 'name_last': 'Last'})

    auth_register_input = {
        'email':'final@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    channel_id = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name': 'name', 'is_public': True}).json()['channel_id']

    handle = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id}).json()['all_members'][0]['handle_str']

    assert handle == "firstlast1"

# Test if function generates handle firstlast00 when given name_first: first, name_last: last0, and firstlast0 already exists
def test_numeric_last_char():
    requests.delete(config.url + '/clear/v1')

    requests.post(config.url + 'auth/register/v2', params={'email': 'valid@gmail.com', 'password': 'password', 'name_first': 'First', 'name_last': 'Last'})
    requests.post(config.url + 'auth/register/v2', params={'email': 'other@gmail.com', 'password': 'password', 'name_first': 'First', 'name_last': 'Last'})

    auth_register_input = {
        'email':'final@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last0'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    channel_id = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name': 'name', 'is_public': True}).json()['channel_id']

    handle = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id}).json()['all_members'][0]['handle_str']

    assert handle == "firstlast00"

# Test if function generates correct handle when more than 10 of the same handle exist
def test_13_duplicate_handles():
    requests.delete(config.url + '/clear/v1')
    requests.post(config.url + 'auth/register/v2', params={'email': 'valid@gmail.com', 'password': 'password', 'name_first': 'First', 'name_last': 'Last'})
    for i in range(11):
        email = str(i) + "@gmail.com"
        requests.post(config.url + 'auth/register/v2', params={'email': email, 'password': 'password', 'name_first': 'First', 'name_last': 'Last'})

    auth_register_input = {
        'email':'11@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    channel_id = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name': 'name', 'is_public': True}).json()['channel_id']

    handle = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id}).json()['all_members'][0]['handle_str']

    assert handle == "firstlast11"