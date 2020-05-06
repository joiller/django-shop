import jwt
from .models import Accounts
from django.http import JsonResponse,JsonResponse


HOME_PAGE = 'http://127.0.0.1:8000'


def identify_account(request):
    # if request.COOKIES['acc']:
    #     acc_code = jwt.decode(request.COOKIES.get('acc'), 'secret', algorithms=['HS256'])
    #     acc = Accounts.objects.get(name=acc_code['name'],password=acc_code['password'])

    acc_code = request.COOKIES['acc']
    if acc_code:
        acc_code = jwt.decode(acc_code,'skey')
        acc = Accounts.objects.filter(
            name=acc_code['name'],
            password=acc_code['password']
        ).first()
        return acc
    else:
        return None


def logged(**kwargs):
    return {
        'success': True,
        'logged': True,
        **kwargs
    }


def unlogged(**kwargs):
    return {
        'success': True,
        'logged': False,
        **kwargs
    }


def failed(message,**kwargs):
    code_list = {
        'ProductOut': 1,
        'MoneyOut': 2
    }
    return {
        'success': False,
        'message': message,
        **kwargs
    }


def success(**kwargs):
    return {
        'success': True,
        **kwargs
    }
