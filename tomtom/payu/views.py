# from django.shortcuts import render

# # Create your views here.
# payu_client_id = "5304451e059e7dfeae7f84e808f4928b124cf2cbfa0babe9953d6f102ac2f3c2"
# payu_client_secret = "167fa91ff70e8926dc42778a8875a2fee21fda2c75964c234db98af10588cd8d"


# # payments/views.py

# from django.conf import settings
# from django.shortcuts import render, redirect
# from .models import Payment
# # import payu_websdk as payu_sdk
# import time

# # payu_client = payu_sdk.PayUClient({
# #     "key": settings.PAYU_MERCHANT_KEY,
# #     "salt": settings.PAYU_MERCHANT_SALT,
# #     "env": settings.PAYU_ENVIRONMENT
# # })

# def payment_request(request):
#     if request.method == 'POST':
#         amount = request.POST['amount']
#         transaction_id = 'Txn' + str(int(time.time()))

#         payment = Payment.objects.create(
#             transaction_id=transaction_id,
#             amount=amount,
#             status='pending'
#         )

#         transaction_data = {
#             'txnid': transaction_id,
#             'amount': str(amount),
#             'productinfo': 'Test Product',
#             'firstname': request.POST['firstname'],
#             'email': request.POST['email'],
#             'phone': request.POST['phone'],
#             'surl': 'http://localhost:8000/payment/success/',
#             'furl': 'http://localhost:8000/payment/failure/',
#             'service_provider': 'payu_paisa'
#         }

#         transaction_data['hash'] = payu_client.generate_hash(transaction_data)

#         return render(request, 'payments/payment_form.html', {'data': transaction_data, 'payu_base_url': settings.PAYU_BASE_URL})

#     return render(request, 'payments/payment_request.html')

# def payment_success(request):
#     # Handle success response
#     return render(request, 'payments/success.html')

# def payment_failure(request):
#     # Handle failure response
#     return render(request, 'payments/failure.html')
