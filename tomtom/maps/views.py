from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import RideForm
from .utils import get_coordinates, haversine
from django.db import IntegrityError
from django.contrib import messages
from django.conf import settings
from .models import Employee, Client, Payment, SampleInvoice
from .forms import EmployeeForm, ClientForm
from django.views.decorators.http import require_GET
import math
import requests
import json
import razorpay
from django.views.decorators.csrf import csrf_exempt
import time
from .models import FCMDevice, PushSubscription

from webpush import send_user_notification


# @csrf_exempt  # For demo purposes only, consider proper CSRF protection in production
# def send_notification(request):
#     if request.method == 'POST':
#         # Assuming you receive the FCM registration ID and message from the request
#         registration_id = request.POST.get('registration_id')
#         message = request.POST.get('message')

#         if registration_id and message:
#             try:
#                 # Create or get the FCM device based on the registration ID
#                 device, created = FCMDevice.objects.get_or_create(registration_id=registration_id)
#                 # Send the message
#                 device.send_message(message)
#                 return JsonResponse({'success': True, 'message': 'Push notification sent successfully'})
#             except Exception as e:
#                 return JsonResponse({'success': False, 'message': str(e)})
#         else:
#             return JsonResponse({'success': False, 'message': 'Missing registration ID or message'})
#     else:
#         return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


def index(request):
    return render(request, 'maps/index.html')

def subscribe(request):
    if request.method == 'POST':
        # Get subscription info from POST request (this will depend on your frontend implementation)
        subscription_info = request.POST.get('subscription_info')
        # user_id = request.user.id  # Example: Get the user ID from the request (assuming user is authenticated)

        # Save the subscription info to your database
        if subscription_info:
            subscription = PushSubscription.objects.create(
                subscription_info=subscription_info
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid subscription data'})
    else:
        return JsonResponse({'error': 'Invalid request'})
    
def send_notification(request):
    if request.method == 'POST':
        # For POC, assume subscription_info is directly provided in the request
        subscription_info = request.POST.get('subscription_info')
        payload = {"head": "Welcome!", "body": "Hello World"}

        try:
            # Send notification to the user
            send_user_notification(subscription_info, payload)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request'})

def payment_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = int(request.POST.get('amount')) * \
            100  # Convert to paise for Razorpay

        # Initialize Razorpay client
        client = razorpay.Client(
            auth=("rzp_test_6CCIFMIjOZytSE", "X4pvs6dYOXjZwcPu4pyr1N4O"))

        # Create Razorpay order

        response_payment = client.order.create(
            dict(amount=amount, currency='INR'))

        print(response_payment)
        order_id = response_payment['id']
        order_status = response_payment['status']
        if order_status == 'created':
            amount = amount / 100  # Convert back to Rupees
            payment = Payment(
                name=name, amount=amount, order_id=order_id)
            payment.save()
            response_payment['name'] = name
            response_payment['email'] = "example@gmail.com"
            return render(request, 'maps/payment_form.html', {'payment': response_payment})

    return render(request, 'maps/payment_form.html')


@csrf_exempt
def payment_status(request):
    response = request.POST
    print(response)
    params_dict = {
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    # client instance
    client = razorpay.Client(
        auth=("rzp_test_6CCIFMIjOZytSE", "X4pvs6dYOXjZwcPu4pyr1N4O"))

    try:
        status = client.utility.verify_payment_signature(params_dict)
        print(status)
        payment = Payment.objects.get(order_id=response['razorpay_order_id'])
        payment.razorpay_payment_id = response['razorpay_payment_id']
        payment.paid = True
        payment.save()
        return render(request, 'maps/payment_status.html', {'status': True})
    except:
        status = "Payment Failed"
        print(status)
    print(response)
    return render(request, 'maps/payment_status.html', {'status': False})

def goto(request):
    return render(request, 'maps/goto.html')

def generate_payment_link(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            amount = int(payload.get('amount', 0)) * 100
            customer_name = payload.get('customer_name', '')

            # Initialize the Razorpay client with your API credentials
            client = razorpay.Client(auth=("rzp_test_6CCIFMIjOZytSE", "X4pvs6dYOXjZwcPu4pyr1N4O"))

            # Create the payment link using the Razorpay API
            response = client.payment_link.create({
                "amount": amount,
                "currency": "INR",
                "customer": {
                    "name": customer_name,
                },
                "callback_url": "http://127.0.0.1:8000/maps/payment_verify_link",
                "callback_method": "get"
            })
            payment_link = response['short_url']

            return JsonResponse({'payment_link': payment_link})

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def verify_payment_link_signature(request):
    
    client = razorpay.Client(auth=("rzp_test_6CCIFMIjOZytSE", "X4pvs6dYOXjZwcPu4pyr1N4O"))
    param_dict = {
        'payment_link_id' : request.GET.get('razorpay_payment_link_id'),
        'payment_link_reference_id' : request.GET.get('razorpay_payment_link_reference_id'),
        'payment_link_status' : request.GET.get('razorpay_payment_link_status'),
        'razorpay_payment_id' : request.GET.get('razorpay_payment_id'),
        'razorpay_signature' : request.GET.get('razorpay_signature'),
    }

    verification = client.utility.verify_payment_link_signature(param_dict)

    if verification:
        # Db related stuff
        return JsonResponse({'success': True, 'Payment_status': 'Payment verified'})

def create_invoice(request):
    return render(request, 'maps/invoice.html')

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.enums import TA_LEFT
from io import BytesIO
from xhtml2pdf import pisa

def generate_invoice(request):
    # Get form data from request
    payload = json.loads(request.body)
    amount = payload.get('amount')
    description = payload.get('description')
    customer_name = payload.get('customer_name')
    payment_link = payload.get('payment_link')

    # Create PDF invoice using ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # Create a PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []

    # Define styles for the payment link
    link_style = ParagraphStyle(name='LinkStyle', fontName='Helvetica', fontSize=12, textColor='blue', alignment=TA_LEFT)

    # Add content to the PDF
    story.append(Paragraph(f'Invoice for: {customer_name}'))
    story.append(Paragraph(f'Amount: {amount} INR'))
    story.append(Paragraph(f'Description: {description}'))

    # Add payment link as a clickable hyperlink
    if payment_link:
        story.append(Paragraph(f'Payment Link'))
        story.append(Paragraph(f'             : <a href="{payment_link}">{payment_link}</a>', link_style))

    # Build the PDF document
    doc.build(story)
    
    return response

from django.template.loader import render_to_string
from pyhtml2pdf import converter
import os
import pdfkit
from django.template.loader import get_template
from django.conf import settings
def generate_sample_invoice(request):
    invoice = {
            "invoice_no": "VT/202324/30",
            "items": [
                {
                    "item_id": 40,
                    "trip_request": {
                        "trip_request_id": "VT00428",
                        "trip_passengers": [
                            {
                                "id": 314,
                                "passenger": {
                                    "passenger_id": 81,
                                    "project_code": "BTG",
                                    "passenger_name": "Rahul",
                                    "gender": "M",
                                    "email_aaddress": "rahul@mail.com",
                                    "country_code": None,
                                    "passenger_contact_number": "7026910602",
                                    "employee_id": "GGJHVY67677"
                                },
                                "feedback": [
                                    {
                                        "feedback_id": 7,
                                        "overall_rating": "2.0",
                                        "driver_feedback": "Unsafe Drop-off",
                                        "vehicle_feedback": "Good Service",
                                        "management_feedback": "Thank you very much for your service and help",
                                        "general_feedback": "",
                                        "fb_photo1": None,
                                        "fb_photo2": None,
                                        "fb_photo3": None,
                                        "created_by": None,
                                        "created_dt": "2024-03-22T04:11:53.673449Z",
                                        "updated_by": None,
                                        "updated_dt": "2024-03-22T04:11:53.673470Z",
                                        "travel_request": 314
                                    }
                                ],
                                "pickup_location": "17, Kalyan Nagar, Bengaluru, Karnataka 560043",
                                "drop_location": "12, Koramangala 8th Block, Bengaluru, 560095",
                                "reporting_time": "2024-03-20T13:30:00Z",
                                "pickup_time": None,
                                "no_of_days": None,
                                "pickup_location_latitude": "13.03743",
                                "pickup_location_langitude": "77.64783",
                                "drop_location_latitude": None,
                                "drop_location_langitude": None,
                                "travel_request_status": "Completed",
                                "travel_request_type": "Drop",
                                "actual_start_time": None,
                                "actual_complete_time": None,
                                "trip_request": "VT00428",
                                "trip_shift": None
                            },
                            {
                                "id": 321,
                                "passenger": {
                                    "passenger_id": 74,
                                    "project_code": "BTG",
                                    "passenger_name": "Virat",
                                    "gender": "M",
                                    "email_aaddress": "shashank.b@itconnectus.com",
                                    "country_code": None,
                                    "passenger_contact_number": "7026910602",
                                    "employee_id": "JBHGHG8783"
                                },
                                "feedback": [],
                                "pickup_location": "17, Kalyan Nagar, Bengaluru, Karnataka 560043",
                                "drop_location": "1518, 17th Main Road, JP Nagar, Bengaluru 560078, Karnataka",
                                "reporting_time": "2024-03-21T13:30:00Z",
                                "pickup_time": None,
                                "no_of_days": None,
                                "pickup_location_latitude": "13.03743",
                                "pickup_location_langitude": "77.64783",
                                "drop_location_latitude": "12.914493409387532",
                                "drop_location_langitude": "77.59147623518174",
                                "travel_request_status": "Completed",
                                "travel_request_type": "Drop",
                                "actual_start_time": None,
                                "actual_complete_time": None,
                                "trip_request": "VT00428",
                                "trip_shift": None
                            }
                        ],
                        "booking_date": "2024-03-21T18:26:34.663000Z",
                        "booked_name": "Ragu",
                        "booked_mobile": "9789763989",
                        "booked_email": "Ragu@gmail.com",
                        "priority": "Employee",
                        "trip_type": "Drop",
                        "trip_status": "InvoiceGenerated",
                        "vehicle_model": "Innova",
                        "trip_time": "2024-03-20T13:30:00Z",
                        "driver_alternate_mobile": "",
                        "meter_reading_opening": 3000,
                        "starting_time": "2024-03-21T23:00:00Z",
                        "meter_reading_closing": 3100,
                        "ending_time": "2024-03-22T04:15:00Z",
                        "total_trip_distance": "100",
                        "total_trip_duration": "5:15",
                        # "extra_distance": "123",
                        "extra_distance": "123",
                        "extra_time": "1",
                        "rate_for_extra_km": "1",
                        "rate_for_extra_hours": "100",
                        "toll": "12",
                        "parking": "10",
                        "entry_tax": "13",
                        "digital_signature_file_name": "http://esafetrip.com/images/trip/signature/sigVT00428.png",
                        "action_status": "",
                        "driver_betta": "0.00",
                        "total_trip_cost": "0.00",
                        "base_price": "0.00",
                        "remarks": "",
                        "active_yn": None,
                        "created_by": "siva",
                        "created_dt": "2024-03-21T18:26:35.411819Z",
                        "updated_by": "siva",
                        "updated_dt": "2024-03-22T04:10:43.656003Z",
                        "client": 6,
                        "project_code": "BTG",
                        "vehicle_number": "KA01MS2324",
                        "driver": 20
                    },
                    "item_details": [],
                    "desc": None,
                    "amount": "0.00",
                    "invoice_no": "VT/202324/30"
                },
                {
                    "item_id": 41,
                    "trip_request": {
                        "trip_request_id": "VT00432",
                        "trip_passengers": [
                            {
                                "id": 322,
                                "passenger": {
                                    "passenger_id": 74,
                                    "project_code": "BTG",
                                    "passenger_name": "Virat",
                                    "gender": "M",
                                    "email_aaddress": "shashank.b@itconnectus.com",
                                    "country_code": None,
                                    "passenger_contact_number": "7026910602",
                                    "employee_id": "JBHGHG8783"
                                },
                                "feedback": [],
                                "pickup_location": "1518, 17th Main Road, JP Nagar, Bengaluru 560078, Karnataka",
                                "drop_location": "17, Kalyan Nagar, Bengaluru, Karnataka 560043",
                                "reporting_time": "2024-03-22T02:30:00Z",
                                "pickup_time": None,
                                "no_of_days": None,
                                "pickup_location_latitude": "12.914493409387532",
                                "pickup_location_langitude": "77.59147623518174",
                                "drop_location_latitude": "13.03743",
                                "drop_location_langitude": "77.64783",
                                "travel_request_status": "Completed",
                                "travel_request_type": "Pickup",
                                "actual_start_time": None,
                                "actual_complete_time": None,
                                "trip_request": "VT00432",
                                "trip_shift": None
                            },
                            {
                                "id": 319,
                                "passenger": {
                                    "passenger_id": 81,
                                    "project_code": "BTG",
                                    "passenger_name": "Rahul",
                                    "gender": "M",
                                    "email_aaddress": "rahul@mail.com",
                                    "country_code": None,
                                    "passenger_contact_number": "7026910602",
                                    "employee_id": "GGJHVY67677"
                                },
                                "feedback": [
                                    {
                                        "feedback_id": 10,
                                        "overall_rating": "3.5",
                                        "driver_feedback": "Bad Map Route, Distracted or Talked on Phone",
                                        "vehicle_feedback": "None",
                                        "management_feedback": "Not pick the call.",
                                        "general_feedback": "Nothing",
                                        "fb_photo1": "http://esafetrip.com/images/fb/319_fb_photo1.jpg",
                                        "fb_photo2": "http://esafetrip.com/images/fb/319_fb_photo2.jpg",
                                        "fb_photo3": "http://esafetrip.com/images/fb/319_fb_photo3.jpg",
                                        "created_by": None,
                                        "created_dt": "2024-03-25T06:48:08.651300Z",
                                        "updated_by": None,
                                        "updated_dt": "2024-03-25T06:48:08.651335Z",
                                        "travel_request": 319
                                    }
                                ],
                                "pickup_location": "12, Koramangala 8th Block, Bengaluru, 560095",
                                "drop_location": "17, Kalyan Nagar, Bengaluru, Karnataka 560043",
                                "reporting_time": "2024-03-22T03:00:00Z",
                                "pickup_time": None,
                                "no_of_days": None,
                                "pickup_location_latitude": None,
                                "pickup_location_langitude": None,
                                "drop_location_latitude": "13.03743",
                                "drop_location_langitude": "77.64783",
                                "travel_request_status": "Completed",
                                "travel_request_type": "Pickup",
                                "actual_start_time": None,
                                "actual_complete_time": None,
                                "trip_request": "VT00432",
                                "trip_shift": None
                            }
                        ],
                        "booking_date": "2024-03-22T12:59:27.730000Z",
                        "booked_name": "Ragu",
                        "booked_mobile": "9789763989",
                        "booked_email": "Ragu@gmail.com",
                        "priority": "Employee",
                        "trip_type": "Pickup",
                        "trip_status": "InvoiceGenerated",
                        "vehicle_model": "Innova",
                        "trip_time": "2024-03-22T02:30:00Z",
                        "driver_alternate_mobile": "",
                        "meter_reading_opening": 0,
                        "starting_time": "2024-03-22T02:30:00Z",
                        "meter_reading_closing": 0,
                        "ending_time": "2024-03-22T13:00:00Z",
                        "total_trip_distance": "",
                        "total_trip_duration": "10:30",
                        # "extra_distance": "",
                        "extra_distance": "123",
                        "extra_time": "",
                        "rate_for_extra_km": "0",
                        "rate_for_extra_hours": "0",
                        "toll": "0.00",
                        "parking": "0.00",
                        "entry_tax": "0.00",
                        "digital_signature_file_name": "http://esafetrip.com/images/trip/signature/sigVT00432.png",
                        "action_status": "",
                        "driver_betta": "0.00",
                        "total_trip_cost": "0.00",
                        "base_price": "0.00",
                        "remarks": "",
                        "active_yn": None,
                        "created_by": "siva",
                        "created_dt": "2024-03-22T12:59:27.301401Z",
                        "updated_by": "siva",
                        "updated_dt": "2024-03-22T13:00:53.397566Z",
                        "client": 6,
                        "project_code": "BTG",
                        "vehicle_number": "KA01MS2324",
                        "driver": 20
                    },
                    "item_details": [],
                    "desc": None,
                    "amount": "0.00",
                    "invoice_no": "VT/202324/30"
                },
                {
                    "item_id": 42,
                    "trip_request": {
                        "trip_request_id": "VT00431",
                        "trip_passengers": [
                            {
                                "id": 317,
                                "passenger": {
                                    "passenger_id": 74,
                                    "project_code": "BTG",
                                    "passenger_name": "Virat",
                                    "gender": "M",
                                    "email_aaddress": "shashank.b@itconnectus.com",
                                    "country_code": None,
                                    "passenger_contact_number": "7026910602",
                                    "employee_id": "JBHGHG8783"
                                },
                                "feedback": [],
                                "pickup_location": "17, Kalyan Nagar, Bengaluru, Karnataka 560043",
                                "drop_location": "1518, 17th Main Road, JP Nagar, Bengaluru 560078, Karnataka",
                                "reporting_time": "2024-03-20T13:30:00Z",
                                "pickup_time": None,
                                "no_of_days": None,
                                "pickup_location_latitude": "13.03743",
                                "pickup_location_langitude": "77.64783",
                                "drop_location_latitude": "12.914493409387532",
                                "drop_location_langitude": "77.59147623518174",
                                "travel_request_status": "Completed",
                                "travel_request_type": "Drop",
                                "actual_start_time": None,
                                "actual_complete_time": None,
                                "trip_request": "VT00431",
                                "trip_shift": None
                            },
                            {
                                "id": 320,
                                "passenger": {
                                    "passenger_id": 81,
                                    "project_code": "BTG",
                                    "passenger_name": "Rahul",
                                    "gender": "M",
                                    "email_aaddress": "rahul@mail.com",
                                    "country_code": None,
                                    "passenger_contact_number": "7026910602",
                                    "employee_id": "GGJHVY67677"
                                },
                                "feedback": [],
                                "pickup_location": "17, Kalyan Nagar, Bengaluru, Karnataka 560043",
                                "drop_location": "12, Koramangala 8th Block, Bengaluru, 560095",
                                "reporting_time": "2024-03-21T13:30:00Z",
                                "pickup_time": None,
                                "no_of_days": None,
                                "pickup_location_latitude": "13.03743",
                                "pickup_location_langitude": "77.64783",
                                "drop_location_latitude": None,
                                "drop_location_langitude": None,
                                "travel_request_status": "Completed",
                                "travel_request_type": "Drop",
                                "actual_start_time": None,
                                "actual_complete_time": None,
                                "trip_request": "VT00431",
                                "trip_shift": None
                            }
                        ],
                        "booking_date": "2024-03-22T12:58:53.984000Z",
                        "booked_name": "Ragu",
                        "booked_mobile": "9789763989",
                        "booked_email": "Ragu@gmail.com",
                        "priority": "Employee",
                        "trip_type": "Drop",
                        "trip_status": "InvoiceGenerated",
                        "vehicle_model": "Innova",
                        "trip_time": "2024-03-20T13:30:00Z",
                        "driver_alternate_mobile": "8866676878",
                        "meter_reading_opening": 0,
                        "starting_time": "2024-03-22T12:00:00Z",
                        "meter_reading_closing": 0,
                        "ending_time": "2024-03-22T13:15:00Z",
                        "total_trip_distance": "",
                        "total_trip_duration": "1:15",
                        # "extra_distance": "",
                        "extra_distance": "123",
                        "extra_time": "",
                        "rate_for_extra_km": "0",
                        "rate_for_extra_hours": "0",
                        "toll": "0.00",
                        "parking": "0.00",
                        "entry_tax": "0.00",
                        "digital_signature_file_name": "http://esafetrip.com/images/trip/signature/sigVT00431.png",
                        "action_status": "",
                        "driver_betta": "0.00",
                        "total_trip_cost": "0.00",
                        "base_price": "0.00",
                        "remarks": "",
                        "active_yn": None,
                        "created_by": "siva",
                        "created_dt": "2024-03-22T12:58:53.574335Z",
                        "updated_by": "siva",
                        "updated_dt": "2024-03-22T13:04:42.299738Z",
                        "client": 6,
                        "project_code": "BTG",
                        "vehicle_number": "KA01MS2324",
                        "driver": 20
                    },
                    "item_details": [],
                    "desc": None,
                    "amount": "0.00",
                    "invoice_no": "VT/202324/30"
                },
                {
                    "item_id": 43,
                    "trip_request": {
                        "trip_request_id": "VT00434",
                        "trip_passengers": [
                            {
                                "id": 323,
                                "passenger": {
                                    "passenger_id": 81,
                                    "project_code": "BTG",
                                    "passenger_name": "Rahul",
                                    "gender": "M",
                                    "email_aaddress": "rahul@mail.com",
                                    "country_code": None,
                                    "passenger_contact_number": "7026910602",
                                    "employee_id": "GGJHVY67677"
                                },
                                "feedback": [],
                                "pickup_location": "17, Kalyan Nagar, Bengaluru, Karnataka 560043",
                                "drop_location": "12, Koramangala 8th Block, Bengaluru, 560095",
                                "reporting_time": "2024-03-25T13:30:00Z",
                                "pickup_time": None,
                                "no_of_days": None,
                                "pickup_location_latitude": "13.03743",
                                "pickup_location_langitude": "77.64783",
                                "drop_location_latitude": None,
                                "drop_location_langitude": None,
                                "travel_request_status": "Completed",
                                "travel_request_type": "Drop",
                                "actual_start_time": None,
                                "actual_complete_time": None,
                                "trip_request": "VT00434",
                                "trip_shift": None
                            },
                            {
                                "id": 324,
                                "passenger": {
                                    "passenger_id": 74,
                                    "project_code": "BTG",
                                    "passenger_name": "Virat",
                                    "gender": "M",
                                    "email_aaddress": "shashank.b@itconnectus.com",
                                    "country_code": None,
                                    "passenger_contact_number": "7026910602",
                                    "employee_id": "JBHGHG8783"
                                },
                                "feedback": [],
                                "pickup_location": "17, Kalyan Nagar, Bengaluru, Karnataka 560043",
                                "drop_location": "4th Main Road, KEB Colony Tavare Kere, BTM Layout I Stage, Bengaluru 560029, Karnataka",
                                "reporting_time": "2024-03-25T13:30:00Z",
                                "pickup_time": None,
                                "no_of_days": None,
                                "pickup_location_latitude": "13.03743",
                                "pickup_location_langitude": "77.64783",
                                "drop_location_latitude": "12.918993606413068",
                                "drop_location_langitude": "77.6062408696086",
                                "travel_request_status": "Completed",
                                "travel_request_type": "Drop",
                                "actual_start_time": None,
                                "actual_complete_time": None,
                                "trip_request": "VT00434",
                                "trip_shift": None
                            },
                            {
                                "id": 325,
                                "passenger": {
                                    "passenger_id": 63,
                                    "project_code": "BTG",
                                    "passenger_name": "RamKumar",
                                    "gender": "M",
                                    "email_aaddress": "ram@gmail.com",
                                    "country_code": None,
                                    "passenger_contact_number": "9789977676",
                                    "employee_id": "BRR656523"
                                },
                                "feedback": [],
                                "pickup_location": "17, Kalyan Nagar, Bengaluru, Karnataka 560043",
                                "drop_location": "Srirampura Road, Kachanaikanahalli, Bengaluru 560099, Karnataka",
                                "reporting_time": "2024-03-25T09:30:00Z",
                                "pickup_time": None,
                                "no_of_days": None,
                                "pickup_location_latitude": "13.03743",
                                "pickup_location_langitude": "77.64783",
                                "drop_location_latitude": "12.80008161108772",
                                "drop_location_langitude": "77.66589684002457",
                                "travel_request_status": "Completed",
                                "travel_request_type": "Drop",
                                "actual_start_time": None,
                                "actual_complete_time": None,
                                "trip_request": "VT00434",
                                "trip_shift": None
                            }
                        ],
                        "booking_date": "2024-03-25T10:40:29.312000Z",
                        "booked_name": "Ragu",
                        "booked_mobile": "9789763989",
                        "booked_email": "Ragu@gmail.com",
                        "priority": "Employee",
                        "trip_type": "Drop",
                        "trip_status": "InvoiceGenerated",
                        "vehicle_model": "Sedan",
                        "trip_time": "2024-03-25T13:30:00Z",
                        "driver_alternate_mobile": "",
                        "meter_reading_opening": 0,
                        "starting_time": "2024-03-25T13:30:00Z",
                        "meter_reading_closing": 0,
                        "ending_time": "2024-03-25T15:30:00Z",
                        "total_trip_distance": "",
                        "total_trip_duration": "2:00",
                        # "extra_distance": "",
                        "extra_distance": "123",
                        "extra_time": "",
                        "rate_for_extra_km": "0",
                        "rate_for_extra_hours": "0",
                        "toll": "0.00",
                        "parking": "0.00",
                        "entry_tax": "0.00",
                        "digital_signature_file_name": "http://esafetrip.com/images/trip/signature/sigVT00434.png",
                        "action_status": "",
                        "driver_betta": "0.00",
                        "total_trip_cost": "1000.00",
                        "base_price": "1000.00",
                        "remarks": "",
                        "active_yn": None,
                        "created_by": "shashank1",
                        "created_dt": "2024-03-25T10:40:30.372370Z",
                        "updated_by": "shashank1",
                        "updated_dt": "2024-03-25T10:46:32.701173Z",
                        "client": 6,
                        "project_code": "BTG",
                        "vehicle_number": "KA45X4567",
                        "driver": 40
                    },
                    "item_details": [],
                    "desc": None,
                    "amount": "0.00",
                    "invoice_no": "VT/202324/30"
                }
            ],
            "invoice_date": "2024-04-18T12:47:47.430367Z",
            "invoice_type": "Date Range",
            "invoice_ref_id": "Client",
            "service": "Rent-A-Cab Operator",
            "period": "2024-3-20,2024-4-30",
            "total_not_taxable": "0.00",
            "total_taxable": "0.00",
            "cgst_percentage": "0.00",
            "sgst_percentage": "0.00",
            "round_off": "0.00",
            "total": "12345",
            "status": "Generated",
            "signed_by": None,
            "created_by": None,
            "created_dt": "2024-04-18T12:47:47.430451Z",
            "updated_by": None,
            "updated_dt": "2024-04-18T12:47:47.430459Z",
            "client": 6
        }

    driver = [
            {
        "driver_id": 20,
        "user": {
            "id": 71,
            "username": "8667350387",
            "password": "pbkdf2_sha256$600000$d3c7vFHALu8a39LBT0G2kf$hjdY9elUgXeSt1x37ddKcsFTQl285w8LqGGVJqXegls=",
            "first_name": "Raj Kumar",
            "last_name": "",
            "email": "",
            "groups": [
                {
                    "id": 5,
                    "name": "Driver"
                }
            ],
            "auth_user_client": []
        },
        "driver_name": "Raj Kumar",
        "driver_contact_number": "8667350387",
        "driver_alternate_contact_number": "",
        "driver_address": "#7",
        "driver_address1": "Ramathapuram",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "537308",
        "licence_id": "IN4565363",
        "licence_validity_dt": None,
        "licence_id_copy": "http://esafetrip.com/images/driver/licence/Raj_Kumar_licence_id_copy.jpg",
        "badge_id": "",
        "badge_validity_dt": None,
        "pan_number": "",
        "pan_copy": None,
        "aadhar_number": "",
        "aadhar_copy": None,
        "driver_photo_copy": None,
        "permanent_address": "",
        "permanent_address1": "",
        "permanent_city": "",
        "permanent_state": "",
        "permanent_pincode": "",
        "status": "Active",
        "reference_name": "",
        "reference_mobile_number": "",
        "otherinfo": "",
        "active_yn": "Y",
        "created_by": "siva",
        "created_dt": "2023-12-30T06:06:58.875791Z",
        "updated_by": "8667350387",
        "updated_dt": "2024-04-10T06:52:10.302910Z"
    },
    {
        "driver_id": 40,
        "user": {
            "id": 70,
            "username": "9789763989",
            "password": "pbkdf2_sha256$600000$Tkyh8z32cDJK8HR8yuUlWw$ZBRe/nH4hOzSZ1ZJ7DHuZDbCrHE79QvSNWEBZ5GKjh4=",
            "first_name": "SIVA",
            "last_name": "",
            "email": "",
            "groups": [
                {
                    "id": 5,
                    "name": "Driver"
                }
            ],
            "auth_user_client": []
        },
        "driver_name": "SIVA",
        "driver_contact_number": "9789763989",
        "driver_alternate_contact_number": "",
        "driver_address": "#234",
        "driver_address1": "Singasandra",
        "city": "Banglore",
        "state": "Karnataka",
        "pincode": "560100",
        "licence_id": "ASD384774",
        "licence_validity_dt": None,
        "licence_id_copy": "http://esafetrip.com/images/driver/licence/SIVA_licence_id_copy.jpg",
        "badge_id": "",
        "badge_validity_dt": None,
        "pan_number": "",
        "pan_copy": None,
        "aadhar_number": "",
        "aadhar_copy": None,
        "driver_photo_copy": None,
        "permanent_address": "",
        "permanent_address1": "",
        "permanent_city": "",
        "permanent_state": "",
        "permanent_pincode": "",
        "status": "Inactive",
        "reference_name": "",
        "reference_mobile_number": "",
        "otherinfo": "",
        "active_yn": "Y",
        "created_by": "siva",
        "created_dt": "2024-02-27T05:58:23.728569Z",
        "updated_by": "9789763989",
        "updated_dt": "2024-04-15T06:20:56.235238Z"
    }
        ]

    client = {
        "client_id": 6,
        "client_name": "Infosys",
        "email_address": "infosis@mail.com",
        "travel_contact_email": "selva.siva@itconnectus.com",
        "travel_contact_number": "9789776484",
        "gst_number": "AA7373373737A",
        "igst_percent": "0.00",
        "cgst_percent": "0.00",
        "sgst_percent": "0.00",
        "gst_type": "Zero-rated",
        "gst_exemption": "",
        "address": "Shantipura main road",
        "address1": "Bengaluru,",
        "pincode": "560100",
        "state": "Karnataka",
        "country_code": "+91",
        "address_lat": "12.846277066988222",
        "address_lan": "77.67916660740855",
        "contact_number": "9789763989",
        "pan_number": "HSGSYS839333",
        "finance_contact_name": "",
        "finance_contact_number": "",
        "nda_dt": None,
        "nda_renewal_dt": None,
        "admin_contact_number": "",
        "admin_contact_name": "",
        "emergency_contact_number": "",
        "zone_code": "",
        "invoice_period_code": None,
        "invoice_signed_by": None,
        "active_yn": None,
        "created_by": "siva",
        "created_dt": "2023-12-19T16:26:17.045178Z",
        "updated_by": "siva",
        "updated_dt": "2024-04-16T04:36:47.723389Z",
        "bank_account_no": None
    }

    bank = {
            "account_no": "123456789",
            "account_name": "Girish",
            "ifsc_code": "HDFC000123",
            "bank_name": "HDFC Bank",
            "branch_name": "Bengaluru",
            "branch_address": "36, shanthipura road, electronicity, Bengaluru",
            "branch_contact": "9789776484",
            "status":None,
            "active_yn": "Y",
            "created_by": "siva",
            "created_dt": "2023-12-19T16:26:17.045178Z",
            "updated_by": "siva",
            "updated_dt": "2023-12-19T16:26:17.045178Z"
        }

    payment_link = "https://rzp.io/i/ehuluMY1cQ"
    # rendered_html = render_to_string('maps/sample_invoice.html', {'invoice': invoice, 'driver': driver, 'client': client, 'bank': bank, 'payment_link':payment_link})
    context = {'invoice': invoice, 'driver': driver, 'client': client, 'bank': bank, 'payment_link':payment_link}
    rendered_html = get_template('maps/sample_invoice.html').render(context)
    # Save the rendered HTML content to a temporary file
    html_filename = 'rendered_template.html'
    html_file_path = os.path.join(settings.BASE_DIR, html_filename)
    with open(html_file_path, 'w') as html_file:
        print("preparing html with backend data")
        html_file.write(rendered_html)

    try:
        # Convert the HTML file to PDF using pyhtml2pdf
        pdf_filename = 'sample.pdf'
        pdf_file_path = os.path.join(settings.BASE_DIR, pdf_filename)

        # Options for wkhtmltopdf
        # options = {
        #     'page-size': 'Letter',
        #     'margin-top': '0.75in',
        #     'margin-right': '0.75in',
        #     'margin-bottom': '0.75in',
        #     'margin-left': '0.75in',
        #     'encoding': "UTF-8",
        # }
        # Specify wkhtmltopdf path in configuration
        config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

        # Convert HTML to PDF using pdfkit
        pdfkit.from_file(html_file_path, pdf_file_path, configuration=config)

        # Add password protection using PyPDF2
        user_password = '12345'
        # owner_password = '1234'
        pdf_file = encrypt_pdf(pdf_file_path, user_password)

        
        print("PDF generated")

        return pdf_file
    except Exception as e:
        print(f"Error generating PDF: {e}")

    #     converter.convert(f'file:///{html_file_path}', pdf_file_path)
    #     print("pdf generated")

    #     # Prepare the response with the PDF content for download
    #     with open(pdf_file_path, 'rb') as pdf_file:
    #         response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    #         response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    #         print("ready to download prepared")
    #         return response
        
    # except Exception as e:
    #     print(f"Error generating PDF: {e}")
    # finally:
    #     # Clean up: Delete the temporary HTML file
    #     if os.path.exists(html_file_path):
    #         print("deleting html file")
    #         os.remove(html_file_path)

        # Create PDF document using ReportLab
    #     response = HttpResponse(content_type='application/pdf')
    #     response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'

    #     # Create PDF from HTML content using pisa
    #     pisa_status = pisa.CreatePDF(
    #         rendered_html, dest=response, encoding='utf-8')
        
    #     if not pisa_status.err:
    #         return response 

    #     # Clean up: Delete the temporary HTML file
    #     if os.path.exists(html_file_path):
    #         os.remove(html_file_path)

    #     return response
    # except Exception as e:
    #     print(f"Error generating PDF: {e}")


    # # Return a response or redirect if needed
    # return HttpResponse("PDF generation failed.")


    # context = {'invoice': invoice, 'driver': driver, 'client': client, 'bank': bank, 'payment_link':payment_link}
    # return render(request, 'maps/sample_invoice.html', context)
from PyPDF2 import *
def encrypt_pdf(pdf_file_path, user_password):
    try:
        encrypted_pdf_path = pdf_file_path.replace('.pdf', '_encrypted.pdf')
        pdf_reader = PdfReader(pdf_file_path)
        pdf_writer = PdfWriter()

        for page_num in range(len(pdf_reader.pages)):  # Use getNumPages() instead of pages
            pdf_writer.add_page(pdf_reader.pages[page_num])

        pdf_writer.encrypt(user_password, use_128bit=True)

        with open(encrypted_pdf_path, 'wb') as encrypted_pdf_file:
            pdf_writer.write(encrypted_pdf_file)

        os.remove(pdf_file_path)
        os.rename(encrypted_pdf_path, pdf_file_path)
        print("PDF encrypted")
        return pdf_file_path
    except Exception as e:
        print(f"Error: {e}")


def ride_request(request):
    if request.method == 'POST':
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)

            # Get coordinates for main pickup and additional pickup locations
            pickup_coords = get_coordinates(ride.pickup_address)
            pickup_coords_1 = get_coordinates(ride.pickup_address_1)
            pickup_coords_2 = get_coordinates(ride.pickup_address_2)
            # Get coordinates for the drop location
            drop_coords = get_coordinates(ride.drop_address)

            # Check if coordinates are available for all pickup locations
            if all([pickup_coords, pickup_coords_1, pickup_coords_2, drop_coords]):
                # Set the coordinates in the Ride object
                ride.pickup_latitude, ride.pickup_longitude = pickup_coords
                ride.pickup_latitude_1, ride.pickup_longitude_1 = pickup_coords_1
                ride.pickup_latitude_2, ride.pickup_longitude_2 = pickup_coords_2
                ride.drop_latitude, ride.drop_longitude = drop_coords

                try:
                    # Save the Ride object
                    ride.save()

                    # Redirect to a success page or handle as needed
                    return redirect('success_page',
                                    pickup_lon=ride.pickup_longitude, pickup_lat=ride.pickup_latitude,
                                    pickup_lon_1=ride.pickup_longitude_1, pickup_lat_1=ride.pickup_latitude_1,
                                    pickup_lon_2=ride.pickup_longitude_2, pickup_lat_2=ride.pickup_latitude_2,
                                    drop_lon=ride.drop_longitude, drop_lat=ride.drop_latitude)
                except IntegrityError as e:
                    # Handle IntegrityError, for example, duplicate entries
                    messages.error(
                        request, 'IntegrityError: {}'.format(str(e)))
            else:
                # Handle the case when coordinates are not available
                messages.error(
                    request, 'Error getting coordinates. Please try again.')
    else:
        form = RideForm()

    return render(request, 'maps/ride_request.html', {'form': form})


def success_page(request, pickup_lon, pickup_lat, pickup_lon_1, pickup_lat_1, pickup_lon_2, pickup_lat_2, drop_lon, drop_lat):
    # Convert parameters to float
    pickup_lon = float(pickup_lon)
    pickup_lat = float(pickup_lat)
    pickup_lon_1 = float(pickup_lon_1)
    pickup_lat_1 = float(pickup_lat_1)
    pickup_lon_2 = float(pickup_lon_2)
    pickup_lat_2 = float(pickup_lat_2)
    drop_lon = float(drop_lon)
    drop_lat = float(drop_lat)

    # Call a function to get the route data
    route_metries = get_optimized_route([pickup_lon, pickup_lat], [pickup_lon_1, pickup_lat_1], [
                                        pickup_lon_2, pickup_lat_2], drop_coords=[drop_lon, drop_lat])

    route_data = get_geojson_data([pickup_lon, pickup_lat], [pickup_lon_1, pickup_lat_1], [
                                  pickup_lon_2, pickup_lat_2], drop_coords=[drop_lon, drop_lat], geojson=route_metries)

    return render(request, 'maps/success_page.html', {
        'pickup_lon': pickup_lon,
        'pickup_lat': pickup_lat,
        'pickup_lon_1': pickup_lon_1,
        'pickup_lat_1': pickup_lat_1,
        'pickup_lon_2': pickup_lon_2,
        'pickup_lat_2': pickup_lat_2,
        'drop_lon': drop_lon,
        'drop_lat': drop_lat,
        'route_data': route_data,
    })


def get_optimized_route(*pickup_coords, drop_coords):
    version_number = 1
    api_key = 'XMnfj9I0Mi7gwOGlLf6MMjGGBTvzIIh6'

    # Prepare the payload for Waypoint Optimization API
    payload = {
        'waypoints': [
            {'point': {'latitude': lat, 'longitude': lon}} for lon, lat in pickup_coords
        ],
        'options': {
            'travelMode': 'car',
        }
    }

    # Include the drop location in the waypoints
    payload['waypoints'].append(
        {'point': {'latitude': drop_coords[1], 'longitude': drop_coords[0]}})

    # TomTom Waypoint Optimization API endpoint
    endpoint = f'https://api.tomtom.com/routing/waypointoptimization/{version_number}'

    # Parameters for the API request
    params = {
        'key': api_key,
    }

    # Convert payload to JSON format
    json_payload = json.dumps(payload)

    # Make the API request with POST method and data using the session
    response = requests.post(endpoint, params=params, data=json_payload, headers={
                             'Content-Type': 'application/json'})

    # Combine pickup coordinates and drop coordinates into a single list
    all_coords = list(pickup_coords) + [drop_coords]

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Check if 'optimizedOrder' is present in the response
        if 'optimizedOrder' in data and data['optimizedOrder']:
            optimized_order = data['optimizedOrder']

            # Draw the route for each pair of locations in the optimized order
            route_geometries = []
            for i in range(len(optimized_order) - 1):
                start_idx, end_idx = optimized_order[i], optimized_order[i + 1]

                # Get the coordinates for the pair
                start_coords, end_coords = all_coords[start_idx], all_coords[end_idx]

                # Calculate the route geometry for the pair
                route_geometry = get_route_geometry(start_coords, end_coords)

                # Append the route geometry to the list
                route_geometries.append(route_geometry)

            return route_geometries
    else:
        # Handle API request failure
        print(response.status_code)
        print(response.text)
        return None


def get_route_geometry(start_coords, end_coords):
    # Replace 'YOUR_API_KEY' with your actual TomTom API key
    api_key = 'XMnfj9I0Mi7gwOGlLf6MMjGGBTvzIIh6'
    # api_key = settings.TOM_API_KEY

    # TomTom Routing API endpoint
    version_number = 1
    locations = f"{start_coords[1]},{start_coords[0]}:{end_coords[1]},{end_coords[0]}"
    content_type = 'json'  # You can change this if needed
    endpoint = f'https://api.tomtom.com/routing/{version_number}/calculateRoute/{locations}/{content_type}'

    # Parameters for the API request
    params = {
        'key': api_key,
        "routeType": "fastest",
        "traffic": "true",
        "instructionsType": "text",
        'computeBestOrder': 'true',  # Optional: Calculate the best order for the waypoints
        'maxAlternatives': 0,       # Optional: Number of alternative routes
        "routeRepresentation": "polyline",
        "computeTravelTimeFor": "all",
        "travelMode": "motorcycle",
    }

    # Make the API request
    response = requests.get(endpoint, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Check if 'routes' is present in the response
        if 'routes' in data and data['routes']:
            route = data['routes'][0]

            # Check if 'legs' is present in the route
            if 'legs' in route and route['legs']:
                leg = route['legs'][0]

                # Check if 'points' is present in the leg
                if 'points' in leg and leg['points']:
                    # Extract latitude and longitude from each point in the 'points' array
                    route_geometry = [
                        [point['longitude'], point['latitude']] for point in leg['points']]
                else:
                    route_geometry = None
            else:
                # Handle the case when 'legs' is not found in the 'routes' section
                route_geometry = None
        else:
            # Handle the case when 'routes' is not found in the data
            route_geometry = None

        return route_geometry
    else:
        # Handle API request failure
        print(response.status_code)
        print(response.text)
        return None


def get_geojson_data(*pickup_coords, drop_coords, geojson):
    # Convert the data to GeoJSON format
    geojson_data = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "LineString",
            "coordinates": geojson
        }
    }

    return {
        'pickup_coords': [[coord[1], coord[0]] for coord in pickup_coords],
        'drop_coords': [drop_coords[1], drop_coords[0]],
        'route_geometry': geojson_data,
    }


def search_location(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        api_key = 'XMnfj9I0Mi7gwOGlLf6MMjGGBTvzIIh6'
        # api_key = settings.TOM_API_KEY

        # Country code for India
        india_country_code = 'IND'
        # search API (TomTom)
        search_api_url = f'https://api.tomtom.com/search/2/search/{query}.json'

        params = {
            'key': api_key,
            'language': 'en-US',
            'countrySet': india_country_code,
        }

        response = requests.get(search_api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            locations = [{
                'name': result.get('address', {}).get('freeformAddress', ''),
                'latitude': result.get('position', {}).get('lat', ''),
                'longitude': result.get('position', {}).get('lon', ''),
            } for result in data.get('results', [])]

            return JsonResponse({'locations': locations})

        return JsonResponse({'error': 'Failed to fetch results'}, status=500)


def emp_list(request):
    employees = Employee.objects.all()
    return render(request, 'maps/emp_list.html', {'employees': employees})


def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')

    else:
        form = EmployeeForm()

    return render(request, 'maps/add_emp.html', {'form': form})


def client_list(request):
    clients = Client.objects.all()
    return render(request, 'maps/client_list.html', {'clients': clients})


def add_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')

    else:
        form = EmployeeForm()

    return render(request, 'maps/add_client.html', {'form': form})


def get_clients(request):
    clients = Client.objects.all()
    client_data = [{'id': client.id, 'name': client.name}
                   for client in clients]
    return JsonResponse({'clients': client_data})


def get_employees(request):
    employees = Employee.objects.all()
    employee_data = [{'id': employee.id, 'name': employee.name}
                     for employee in employees]
    return JsonResponse({'employees': employee_data})


def get_client_details(request, pk):
    if request.method == 'GET':
        try:
            client = get_object_or_404(Client, pk=pk)
            client_details = {
                'id': client.id,
                'address': client.address,
                'latitude': float(client.latitude) if client.latitude is not None else None,
                'longitude': float(client.longitude) if client.longitude is not None else None,
            }
            return JsonResponse(client_details)
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Client not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_employee_details(request, pk):
    if request.method == 'GET':
        try:
            employee = get_object_or_404(Employee, pk=pk)
            employee_details = {
                'id': employee.id,
                'emp_id': employee.emp_id,
                'name': employee.name,
                'address': employee.address,
                'longitude': float(employee.longitude) if employee.longitude is not None else None,
                'latitude': float(employee.latitude) if employee.latitude is not None else None,
            }

            return JsonResponse(employee_details)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@require_GET
def get_nearby_employees(request):

    pickup_coords = [request.GET.get(
        'pickup_lon'), request.GET.get('pickup_lat')]
    drop_coords = [request.GET.get('drop_lon'), request.GET.get('drop_lat')]

    # Check if coordinates are valid
    if None in pickup_coords or None in drop_coords:
        print(
            f"Invalid coordinates - Pickup: {pickup_coords}, Drop: {drop_coords}")
        return JsonResponse({'error': 'Invalid coordinates'})
    # Convert coordinates to floats for further processing
    pickup_coords = [float(coord) for coord in pickup_coords]
    drop_coords = [float(coord) for coord in drop_coords]

    # Ensure that the coordinates are valid floats
    if any(math.isnan(coord) for coord in pickup_coords) or any(math.isnan(coord) for coord in drop_coords):
        print(
            f"Invalid coordinates after conversion to floats - Pickup: {pickup_coords}, Drop: {drop_coords}")
        return JsonResponse({'error': 'Invalid coordinates'})

    nearby_employees = Employee.objects.all()

    for employee in nearby_employees:
        employee.latitude = float(employee.latitude)
        employee.longitude = float(employee.longitude)

    radius_km = 5  # Adjust the radius as needed

    # Filter employees based on haversine distance
    filtered_employees = [
        employee for employee in nearby_employees
        if haversine(employee.latitude, employee.longitude, pickup_coords[1], pickup_coords[0]) <= radius_km
    ][:5]

    # Add print statements to debug the values of each employee
    for employee in filtered_employees:
        print(
            f"Employee Name: {employee.name}, Latitude: {employee.latitude}, Longitude: {employee.longitude}")

    # Create a list of dictionaries containing employee details
    nearby_employees_list = [
        {
            'name': employee.name,
            'latitude': employee.latitude,
            'longitude': employee.longitude,
        }
        for employee in filtered_employees
    ]

    return JsonResponse({'nearby_employees': nearby_employees_list})


def get_nearby_clients(request):
    pass

