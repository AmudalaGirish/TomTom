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
import os
from pywebpush import webpush, WebPushException



def index(request):
    return render(request, 'maps/index.html')

def subscribe(request):
    if request.method == 'POST':
        # Get subscription info from POST request (this will depend on your frontend implementation)
        data = json.loads(request.body)
        print('data:', data)
        subscription_info = data.get('subscription_info')
        print('subscription_info:', subscription_info)
        # user_id = request.user.id  # Example: Get the user ID from the request (assuming user is authenticated)
        user_id = 1  # Example: Hard-coded user ID

        # Save the subscription info to your database
        if subscription_info and user_id is not None:
            subscription, created = PushSubscription.objects.update_or_create(
                user_id=user_id,
                defaults={'subscription_info': subscription_info}
            )

            if created:
                print("A new subscription was created.")
            else:
                print("An existing subscription was updated.")

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid subscription data'})
    else:
        return JsonResponse({'error': 'Invalid request'})
    
def send_notification(request):
    if request.method == 'POST':
        data = json.loads(request.body) # 
        # subscription_info = data.get('subscription_info')
        # payload = data.get('payload', {})
        user_id = 1 # data.get('user_id')

        if user_id is not None:
            try:
                subscription = PushSubscription.objects.get(user_id=user_id)
                subscription_info = subscription.subscription_info

                vapid_private_key = settings.VAPID_PRIVATE_KEY
                webpush(
                    subscription_info=subscription_info,
                    data="Hello, trip is @7PM", # json.dumps(payload), #
                    vapid_private_key=vapid_private_key,
                    vapid_claims={
                        "sub": settings.VAPID_EMAIL,
                    }
                )
                print('webpush')
                return JsonResponse({'success': True})
            
            except WebPushException as ex:
                print("Error:", ex)
                # Mozilla returns additional information in the body of the response.
                if ex.response and ex.response.json():
                    extra = ex.response.json()
                    print("Remote service replied with a {}:{}, {}",
                        extra.code,
                        extra.errno,
                        extra.message
                        )
        else:
            return JsonResponse({'error': 'Subscription info missing'})
    else:
        return JsonResponse({'error': 'Invalid request method'})

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
            print("payment_link:", payment_link)

            return JsonResponse({'payment_link': payment_link})

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def verify_payment_link_signature(request):
    print("inside payment link signature")
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
        print("payment verified and paid through link")
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
    invoice =     {
        "invoice_no": "VT/202324/62",
        "items": [
            {
                "item_id": 106,
                "trip_request": None,
                "item_details": [],
                "desc": "Transportation Charges For Emplyees For the Month of May 2024",
                "amount": "7000.00",
                "taxable": "N",
                "invoice_no": "VT/202324/62"
            },
            {
                "item_id": 107,
                "trip_request": None,
                "item_details": [],
                "desc": "CGST @ 2.00",
                "amount": "120.00",
                "taxable": "N",
                "invoice_no": "VT/202324/62"
            },
            {
                "item_id": 108,
                "trip_request": None,
                "item_details": [],
                "desc": "SGST @ 2.00",
                "amount": "120.00",
                "taxable": "N",
                "invoice_no": "VT/202324/62"
            }
        ],
        "invoice_date": "2024-05-23T11:53:31.344399Z",
        "invoice_type": "Date Range",
        "invoice_ref_id": None,
        "po_no": "89464944434",
        "service": "Rent-A-Cab Operator",
        "period": "01-05-2024 to 31-05-2024",
        "total_not_taxable": "7240.00",
        "total_taxable": "0.00",
        "cgst_percentage": "2.00",
        "sgst_percentage": "2.00",
        "round_off": "0.00",
        "total": "7240.00",
        "status": "MailSent",
        "signed_by": "SIVA",
        "invoice_file_link": "http://esafetrip.com/pdf/invoices/invoice_CB3QaGn.pdf",
        "created_by": None,
        "created_dt": "2024-05-23T11:53:31.344499Z",
        "updated_by": None,
        "updated_dt": "2024-05-23T11:54:06.515053Z",
        "client": 1,
        "project_code": None
    }

    driver = [
           {
    "driver_id": 1,
    "user": {
        "id": 2,
        "username": "8667350387",
        "password": "pbkdf2_sha256$600000$jbC1sKsRIx9XpP9RZCOROC$FhEZZ0ezvnc004u4uDCwKz2O2q544UHaqFLQU/l4dCQ=",
        "first_name": "SELVASIVA",
        "last_name": "CHANDRAN",
        "email": "selva.siva@itconnectus.com",
        "groups": [
            {
                "id": 5,
                "name": "Driver"
            }
        ],
        "auth_user_client": [
            {
                "client_auth_id": 2,
                "client": 1,
                "user": 2
            }
        ]
    },
    "driver_name": "SELVASIVA CANDRAN.S",
    "driver_contact_number": "8667350387",
    "driver_alternate_contact_number": "9789763989",
    "driver_address": "Attibele Rayakottai Road,",
    "driver_address1": "Arehalli (Anekal)",
    "city": "Bengaluru",
    "state": "Karnataka",
    "pincode": "562107",
    "licence_id": "KA99 20190000293",
    "licence_validity_dt": "2027-12-12",
    "licence_id_copy": "http://esafetrip.com/images/driver/licence/SELVASIVA_CANDRAN.S_licence_id_copy.jpg",
    "badge_id": "E8298289237",
    "badge_validity_dt": "2028-10-03",
    "pan_number": "KNEP8729B1",
    "pan_copy": "http://esafetrip.com/images/driver/pan/SELVASIVA_CANDRAN.S_pan_copy.jpg",
    "aadhar_number": "110210108928",
    "aadhar_copy": "http://esafetrip.com/images/driver/id/SELVASIVA_CANDRAN.S_aadhar_copy.jpg",
    "driver_photo_copy": "http://esafetrip.com/images/driver/photo/SELVASIVA_CANDRAN.S_driver_photo_copy.jpg",
    "permanent_address": "903/19, Barlina Road",
    "permanent_address1": "Shrirama Nagar",
    "permanent_city": "Tumakuru",
    "permanent_state": "Karnataka",
    "permanent_pincode": "572101",
    "status": "Inactive",
    "reference_name": "SHASHANK",
    "reference_mobile_number": "7026910602",
    "otherinfo": "NA",
    "active_yn": "Y",
    "created_by": "siva",
    "created_dt": "2024-05-03T05:59:19.524653Z",
    "updated_by": "8667350387",
    "updated_dt": "2024-05-14T13:45:12.484894Z"
},
{
    "driver_id": 2,
    "user": {
        "id": 7,
        "username": "7026910602",
        "password": "pbkdf2_sha256$600000$aJX9Dz01qLwrE1PmV9uIKe$Kg1icU0s4aJdqP1hTTxFxCRWXDNugTE7crkQlDgx2dw=",
        "first_name": "SHASHANK",
        "last_name": "GOWDA",
        "email": "shashank.b@itconnectus.com",
        "groups": [
            {
                "id": 5,
                "name": "Driver"
            }
        ],
        "auth_user_client": [
            {
                "client_auth_id": 4,
                "client": 1,
                "user": 7
            }
        ]
    },
    "driver_name": "Shashank Gowda",
    "driver_contact_number": "7026910602",
    "driver_alternate_contact_number": "8667350387",
    "driver_address": "1st Main Road,",
    "driver_address1": "Bommasandra,",
    "city": "Bengaluru",
    "state": "Karnataka",
    "pincode": "560099",
    "licence_id": "KA7648487472",
    "licence_validity_dt": "2026-06-13",
    "licence_id_copy": "http://esafetrip.com/images/driver/licence/SHASHANK.B_licence_id_copy.jpg",
    "badge_id": "BD3783232",
    "badge_validity_dt": "2026-05-09",
    "pan_number": "KNEP000D733",
    "pan_copy": "http://esafetrip.com/images/driver/pan/SHASHANK.B_pan_copy.jpg",
    "aadhar_number": "110210102733",
    "aadhar_copy": "http://esafetrip.com/images/driver/id/SHASHANK.B_aadhar_copy.jpg",
    "driver_photo_copy": "http://esafetrip.com/images/driver/photo/SHASHANK.B_driver_photo_copy.jpg",
    "permanent_address": "Gokulam 2nd Stage 2nd Main Road,",
    "permanent_address1": "Gokulam 2nd Stage, Gokulam,",
    "permanent_city": "Mysuru",
    "permanent_state": "Karnataka",
    "permanent_pincode": "570017",
    "status": "Inactive",
    "reference_name": "SIVA",
    "reference_mobile_number": "9789763989",
    "otherinfo": "NA",
    "active_yn": "Y",
    "created_by": "siva",
    "created_dt": "2024-05-09T06:13:41.351479Z",
    "updated_by": "7026910602",
    "updated_dt": "2024-05-14T11:41:08.779468Z"
},
        ]

    client = {
        "client_id": 1,
        "client_name": "CADENCE DESIGN SYSTEMS (INDIA) PVT LTD",
        "email_address": "shashank.b@itconnectus.com",
        "travel_contact_email": "selva.siva@itconnectus.com",
        "travel_contact_number": "8667350387",
        "gst_number": "29AAACC1138Q1ZE",
        "igst_percent": "2.50",
        "cgst_percent": "2.00",
        "sgst_percent": "2.00",
        "gst_type": "Exempt",
        "gst_exemption": "Yes",
        "address": "RMZ Ecoworld Rd,Adarsh Palm Retreat,",
        "address1": "Bellandur, Bengaluru,",
        "pincode": "560103",
        "state": "Kanataka",
        "country_code": "+91",
        "address_lat": "12.9263",
        "address_lan": "77.68116",
        "contact_number": "9789763989",
        "pan_number": "KNEPS98801",
        "finance_contact_name": "SHASHANK",
        "finance_contact_number": "7026910602",
        "nda_dt": "2025-06-27",
        "nda_renewal_dt": "2029-05-31",
        "admin_contact_number": "7026910602",
        "admin_contact_name": "SHASHANK.B",
        "emergency_contact_number": "9789763989",
        "zone_code": "C-1",
        "invoice_period_code": "weekly",
        "invoice_signed_by": "SIVA",
        "active_yn": None,
        "created_by": "siva",
        "created_dt": "2024-05-03T07:46:21.740635Z",
        "updated_by": "siva",
        "updated_dt": "2024-05-22T11:47:32.517706Z",
        "bank_account_no": "1102101026425"
    }

    bank = {
            "account_no": "1102101026425",
            "account_name": "SELVASIVACHANDRAN.S",
            "ifsc_code": "CNRB0001102",
            "bank_name": "CANARA BANK",
            "branch_name": "ARUMUGANERI",
            "branch_address": "Main Road, Arumuganeri-628202",
            "branch_contact": "9789763989",
            "status": None,
            "active_yn": None,
            "created_by": None,
            "created_dt": "2024-05-03T07:38:21.164860Z",
            "updated_by": None,
            "updated_dt": "2024-05-03T07:38:21.164882Z"
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

