from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="twdv64kb25vmx2h3",
        public_key="yqmd5tc7kc4k6nvd",
        private_key="64c1b0d90342975be33e28ceb5bb0b80"
    )
)

def validate_user_session(id, token):
    UserModel = get_user_model()

    try:
        user = UserModel.objects.get(pk=id)

        if user.session_token == token:
            return True
        return False
    except UserModel.DoesNotExist:
        return False

@csrf_exempt
def generate_token(request, id, token):
    if not validate_user_session(id, token):
        return JsonResponse({'error' : 'invalid'})

    return JsonResponse({'clientToken': gateway.client_token.generate(),'success': 'true'})


@csrf_exempt
def process_payment(request, id, token):
    if not validate_user_session(id, token):
        return JsonResponse({'error': 'invalid'})
    
    nonce_from_the_client = request.POST["paymentMethodNonce"]
    amount_from_the_client = request.POST["amount"]


    result = gateway.transcation.sale({
        "amount" : amount_from_the_client,
        "payment_method_nonce" : nonce_from_the_client,
        "options" : {
            "submit_for_settelment": True
        }
    })

    if result.is_sucess:
        return JsonResponse({'sucess': result.is_sucess,
        'transcation':{'id':result.transcation.id}})
