from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store
import re
import urllib.request
from PIL import Image
regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

def users_all_v1(token):
    '''
    users_all_v1: Returns a list of all users and their associated details.

    Arguments:
        token  - str    - token of the user

    Exceptions: 
        AccessError - Occurs when token is invalid

    Return Value:
        Returns a dictionary contains list of users
        For example: { 'users': 
            [
            {'u_id': 1, 
            'email': 'abcd@unsw.edu.au', 
            'name_first': 'name', 
            'name_last': 'name', 
            'handle_str': handle_str}, 
            ]
        }
    '''

    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    validate_token(token)
    # get a list of user
    store = data_store.get()

    list_of_user = []
    for user in store['users']:
            list_of_user.append(
                {
                    'u_id': user['id'],
                    'email': user['email'],
                    'name_first': user['name_first'],
                    'name_last': user['name_last'],
                    'handle_str': user['handle_str']
                }
            )

    return {'users': list_of_user}


def user_profile_v1(token, u_id):
    '''
    users_profile_v1: For a valid user, returns information about their
                        user_id, email, first name, last name, and handle

    Arguments:
        token  - string    - token of the user
        u_id   - integer   - autg_user_id of the user

    Exceptions: 
        AccessError - Occurs when token is invalid
        InputError  - Occurs when u_id does not refer to a valid user

    Return Value:
        Returns a dictionary contains list of users
        For example: { 'user': 
            {'u_id': 1, 
            'email': 'abcd@unsw.edu.au',
            'name_first': 'name', 
            'name_last': 'name', 
            'handle_str': handle_str},
        }                     
    '''
    store = data_store.get()
    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    validate_token(token)
    user = [user for user in (store['users'] + store['removed_users']) if user['id'] == u_id]
    if user == []:
        raise InputError(description="Invalid u_id")

    user = user[0]
    return {'user': 
        {
        'u_id': user['id'],
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str']
        }
    }


def user_profile_setname_v1(token, name_first, name_last):
    '''
    user_profile_setname_v1: Update the authorised user's first and last name

    Arguments:
        token       - string    - token of the user
        name_first  - string    - firstname of the user
        name_last   - string    - lastname of the user

    Exceptions: 
        AccessError - token is invalid
        InputError  - length of name_first or name_last is not
                      between 1 and 50 characters inclusive
                    
    Return Value:
        Returns {}
    '''
    
    
    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    u_id = validate_token(token)['user_id']
    
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="Invalid name_first length")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="Invalid name_last length")

    store = data_store.get()
    for user_index in range(len(store['users'])):
        if store['users'][user_index]['id'] == u_id:
            if store['users'][user_index]['name_first'] == name_first and \
                store['users'][user_index]['name_last'] == name_last:
                raise InputError(description="same name_as previous")
            store['users'][user_index]['name_first'] = name_first
            store['users'][user_index]['name_last'] = name_last
    data_store.set(store)
    return {}

def user_profile_setemail_v1(token, email):
    '''
    user_profile_setemail_v1: Update the authorised user's first and last name

    Arguments:
        token       - string    - token of the user
        email       - string    - email of the user

    Exceptions: 
        AccessError - token is invalid
        InputError  - email entered is not a valid email (more in section 6.4)
                    - email address is already being used by another user

    Return Value:
        Returns {}
    '''


    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    u_id = validate_token(token)['user_id']

    # Checking if email is valid
    if not re.fullmatch(regex, email):
        raise InputError(description="Invalid email")

    email_of_current_user = filter_data_store(store_list='users', key='id', value = u_id)[0]['email']
    if email_of_current_user == email:
        raise InputError (description="email is the same as previous")

    email_list = filter_data_store(store_list='users', key='email')
    # if email_list == None:
    #    raise InputError(description="No valid email yet")
    if email in email_list:
        raise InputError (description="email is used by other user")

    store = data_store.get()
    for user_index in range(len(store['users'])):
        if store['users'][user_index]['id'] == u_id:
            store['users'][user_index]['email'] = email
    data_store.set(store)
    return {}


def user_profile_sethandle_v1(token, handle):
    '''
    user_profile_sethandle_v1: Update the authorised user's first and last name

    Arguments:
        token   - string    - token of the user
        handle  - string    - handle of the user

    Exceptions: 
        AccessError - token is invalid
        InputError  - length of handle_str is not between 3 and 20 characters inclusive
                    - handle_str contains characters that are not alphanumeric
                    - the handle is already used by another user


    Return Value:
        Returns {}
    '''

    
    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    u_id = validate_token(token)['user_id']

    # Checking if handle is valid
    if len(handle) < 3 or len(handle) > 20:
        raise InputError(description='Invalid handle length')
    if not handle.isalnum():
        raise InputError(description='handle contains char that are not alphanumeric')


    handle_of_current_user = filter_data_store(store_list='users', key='id', value = u_id)[0]['handle_str']
    if handle_of_current_user == handle:
        raise InputError (description="handle is the same as previous")

    handle_list = filter_data_store(store_list='users', key='handle_str')
    # if handle_list == None:
    #   raise InputError(description="No valid handle_str yet")
    if handle in handle_list:
        raise InputError (description="handle_str is used by other user")

    store = data_store.get()
    for user_index in range(len(store['users'])):
        if store['users'][user_index]['id'] == u_id:
            store['users'][user_index]['handle_str'] = handle
    data_store.set(store)
    return {}

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):    
    if not img_url.endswith(".jpg"):
        raise InputError(description='Image uploaded is not a JPG')

    if x_end < x_start:
        raise InputError(description='x_end is less than x_start')

    if y_end < y_start:
        raise InputError(description='y_end is less than y_start')

    if x_start < 0 or y_start < 0:
        raise InputError(description='Given dimensions are not within the dimensions of the image at the URL')

    u_id = validate_token(token)['user_id']

    urllib.request.urlretrieve(img_url, f"images/{u_id}.jpg")

    image_object = Image.open(f"images/{u_id}.jpg")

    width, height = image_object.size

    if x_end > width or y_end > height:
        raise InputError(description='Given dimensions are not within the dimensions of the image at the URL')

    cropped_image = image_object.crop((x_start, y_start, x_end, y_end))

    cropped_image.save(f"images/{u_id}.jpg")

    return {}
