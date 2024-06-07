from django.conf import settings
import requests


def generate_access_token():
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
    response = requests.post(
        f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token",
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        data={"grant_type": "client_credentials"},
        auth=auth,
    )
    return response.json().get("access_token")