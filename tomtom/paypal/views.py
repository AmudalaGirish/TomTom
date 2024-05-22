from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import requests
from .models import Transaction_paypal

def checkout_view(request):
    return render(request, 'paypal/checkout.html')


def generate_access_token():
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
    response = requests.post(
        f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token",
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        data={"grant_type": "client_credentials"},
        auth=auth,
    )
    return response.json().get("access_token")

def create_order(request):
    if request.method == "POST":

        # Extract invoice_id from the request
        # invoice_id = request.POST.get('invoice_id')
        invoice_id = "1234"
        currency_code = "USD"
        value = "100.00"
        if not invoice_id:
            return JsonResponse({"error": "Invoice ID is required."}, status=400)
        
        access_token = generate_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        data = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": currency_code,
                    "value": value
                }
            }]
        }
        response = requests.post(
            f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders",
            json=data,
            headers=headers,
        )
        order_data = response.json()
        if response.status_code == 201:
            Transaction_paypal.objects.create(
                invoice_id=invoice_id,
                order_id=order_data['id'],
                amount=value,
                currency=currency_code,
                order_status=order_data['status'],
            )
            
        return JsonResponse(response.json(), status=response.status_code)
    return JsonResponse({"error": "Invalid request method."}, status=400)

def capture_order(request, order_id):
    if request.method == "POST":
        access_token = generate_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.post(
            f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture",
            headers=headers,
        )

        order_data = response.json()

        if response.status_code == 201:
            transaction = order_data['purchase_units'][0]['payments']['captures'][0]
            try:
                paypal_transaction = Transaction_paypal.objects.get(order_id=order_id)
                paypal_transaction.transaction_id = transaction['id']
                paypal_transaction.order_status = order_data['status']
                paypal_transaction.transaction_status = transaction['status']
                paypal_transaction.save()
            except Transaction_paypal.DoesNotExist:
                return JsonResponse({"error": "Transaction not found."}, status=404)
            
        return JsonResponse(order_data, status=response.status_code)
    return JsonResponse({"error": "Invalid request method."}, status=400)
