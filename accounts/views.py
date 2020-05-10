from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *
import jwt
from .utils import *
from django.db import transaction, IntegrityError
import uuid
from django.db.models.functions import Coalesce

# Create your views here.

HOME_PAGE = 'http://127.0.0.1:8000'


def home(req):
    return render(req, 'accounts/main.html')


def products(request):
    if request.method == 'GET':
        prods = Products.objects.all()
        ps = list(map(lambda x: {
            'id': x.id,
            'name': x.name,
            'price': x.price,
            'volume': x.volume
        }, prods))
        print(dir(prods[0]))
        return JsonResponse(success(
            prods=ps
        ))
    return HttpResponse('products')


def transactions(request, category):
    acc = identify_account(request)
    if not acc:
        return JsonResponse(unlogged())
    categories = {
        PurchasesPoly: 'purchase',
        ChargesPoly: 'charge',
        ExtractionsPoly: 'extraction'
    }
    if category == 0:
        trans = TransactionsPoly.objects.filter(account=acc).order_by('-updated_at')

        ts = list(map(
            lambda x: {
                'id': x.id,
                'created_at': x.created_at,
                'updated_at': x.updated_at,
                'category': categories[x.get_real_instance_class()]
            },trans
        ))
        return JsonResponse(success(
            transactions=ts
        ))
    elif category == 1 or category==2 or category==3:
        category = {
            1: ChargesPoly,
            2: PurchasesPoly,
            3: ExtractionsPoly
                    }[category]
        trans = TransactionsPoly.objects.instance_of(category)\
            .filter(account=acc).order_by('-updated_at')
        ts = list(map(
            lambda x: {
                'id': x.id,
                'created_at': x.created_at,
                'updated_at': x.updated_at,
                'category': categories[category]
            }, trans
        ))
        return JsonResponse(success(
            transactions=ts
        ))
    else:
        pass

    return HttpResponse(11)


def accounts(req):
    return HttpResponse(str(req))


def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        password = request.POST['password']
        exists = Accounts.objects.filter(name=name)
        if exists:
            return JsonResponse(failed(
                'UsernameExists'
            ))
        try:
            with transaction.atomic():
                acc = Accounts(
                    name=name,
                    password=password
                )
                acc.save()
        except IntegrityError as err:
            return JsonResponse(failed(
                'DatabaseError'
            ))
        return JsonResponse(success(
            name=acc.name
        ))


def login(request):
    if request.method == 'GET':
        acc = identify_account(request)
        # acc_code = request.COOKIES['acc']
        # if acc_code: # redirect to referer with account name
        #     acc_code = jwt.decode(acc_code,'skey')
        #     acc = Accounts.objects.filter(name=acc_code['name'],password=2)
        if acc:
            return JsonResponse({
                'success': True,
                'logged': True,
                'name': acc.name,
                'referer': request.headers['referer'] or HOME_PAGE
            })
        else:
            return JsonResponse({
                'success': True,
                'logged': False,
                'referer': request.headers['referer'] or HOME_PAGE
            })

    elif request.method == 'POST':
        # give the jwt code about: name and password
        # or set-cookie
        acc = {
            'name': 'jhl',
            'password': 'jhl'
        }
        cok = jwt.encode(acc, 'skey')
        return JsonResponse({
            'success': True,
            'cok': cok.decode()
        })


def homepage(request):
    if request.method == 'GET':
        acc = identify_account(request)
        if acc:
            return JsonResponse(logged(
                referer=HOME_PAGE,
                name=acc.name
            ))
        return JsonResponse(unlogged(
            logged=False,
            referer=HOME_PAGE
        ))


def purchase(request):
    if request.method == 'POST':
        acc = identify_account(request)
        if acc:
            product = Products.objects.filter(id=request.POST['product_id'])
            if product:
                product = product.first()
                req_volume = int(request.POST['volume'])
                volume = product.volume
                if req_volume > volume:
                    return JsonResponse(failed(
                        'ProductOut'

                    ))
                else:
                    total = product.price * req_volume
                    if acc.balance < total:
                        return JsonResponse(failed(
                            'MoneyOut'

                        ))
                    else:
                        try:
                            with transaction.atomic():
                                acc.balance -= total
                                acc.save()

                                product.volume -= req_volume
                                product.save()

                                p = PurchasesPoly(
                                    amount=total,
                                    volume=req_volume,
                                    account=acc,
                                    product=product,
                                    transation_number=str(uuid.uuid4())
                                )
                                p.save()

                                # t = Transactions(
                                #     category=1,
                                #     category_id=p.id,
                                #     account=acc
                                # )
                                # t.save()
                                print('product:', product)
                                print('account:', acc)
                                print('purchase:', p)
                                # print('t:',t)

                        except IntegrityError:
                            # change return  false
                            return JsonResponse(failed(
                                'DataBaseError',
                                balance=acc.balance
                            ))

                        else:
                            return JsonResponse(logged(
                                balance=acc.balance,
                                volume=p.volume,
                                amount=p.amount,
                                product=p.product.name
                            ))
            else:
                return JsonResponse(failed(
                    'NoSuchProduct'
                ))

        else:
            return JsonResponse(unlogged(
                referer=HOME_PAGE + '/api/login/'
            ))


def refund(request):
    if request.method == 'POST':
        acc = identify_account(request)
        if not acc:
            return JsonResponse(unlogged())
        transaction_id = request.POST['transaction_id']
        t = TransactionsPoly.objects.get(id=transaction_id)
        try:
            with transaction.atomic():
                if type(t) == ChargesPoly:
                    nt = t
                    nt.status = 1  # 退款记录
                    t.status = 2  # 原记录失效
                    nt.save()
                    t.save()

                    # 余额取消
                    if acc.balance < t.amount:
                        raise IntegrityError
                    acc.balance -= t.amount
                    acc.save()

                    '''返还到卡'''

                elif type(t) == PurchasesPoly:
                    nt = t
                    nt.status = 1
                    t.status = 2
                    nt.save()
                    t.save()

                    # 产品返还
                    t.product.volume += t.volume
                    t.product.save()

                elif type(t) == RefundsPoly:
                    pass
                elif type(t) == ExtractionsPoly:
                    nt = t
                    nt.status = 1  # 退款记录
                    t.status = 2  # 原记录失效
                    nt.save()
                    t.save()

                    # 余额取消
                    if acc.balance < t.amount:
                        raise IntegrityError
                    acc.balance += t.amount
                    acc.save()

                    '''重新拿钱'''

        except IntegrityError:
            return JsonResponse(failed('IntegrityError'))

        else:
            return JsonResponse(
                logged(

                )
            )


def helper(request):
    p = ChargesPoly.objects.last()
    print('amount:', p.amount)
    print('id:', p.id)
    print(p.transactionspoly_ptr_id)

    return HttpResponse('okokok')


def charge(request):
    if request.method == 'POST':
        acc = identify_account(request)
        if not acc:
            print('noacc')
            return JsonResponse(unlogged())
        try:
            with transaction.atomic():
                print('amount:', type(request.POST['amount']))
                print('card:', type(request.POST['from_card']))
                amount = float(request.POST['amount'])
                from_card = request.POST['from_card']

                acc.balance += amount
                acc.save()

                c = ChargesPoly(
                    account=acc,
                    amount=amount,
                    from_card=from_card,
                    transation_number=str(uuid.uuid4())
                )
                c.save()
        except IntegrityError as err:
            print('err')
            print(err)
            return JsonResponse(failed('IntegrityError'))

        else:
            print('okk')
            return JsonResponse(logged(
                amout=c.amount,
                from_card=c.from_card
            ))


def extract(request):
    acc = identify_account(request)

    if not acc:
        return JsonResponse(unlogged())

    amount = float(request.POST['amount'])
    to_card = request.POST['to_card']

    if amount > acc.balance:
        return JsonResponse(failed(
            'MoneyOut'
        ))

    try:
        with transaction.atomic():
            acc.balance -= amount
            acc.save()

            e = ExtractionsPoly(
                account=acc,
                amount=amount,
                to_card=to_card,
                transation_number=str(uuid.uuid4())
            )
            e.save()

    except IntegrityError as err:
        print(err)
        return JsonResponse(failed('IntegrityError'))

    else:
        return JsonResponse(logged(
            amount=e.amount,
            to_card=e.to_card
        ))
