from django.shortcuts import render

# Create your views here.

class TripNotification(APIView):

    def post(self, request):
        # Retrieve trip_id from request data
        # trip_id = request.data.get('trip_id')
        trip_id = 'VT00076'

        if not trip_id:
            return Response({'error': 'Trip ID Required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch trip details from database
            trip = TblTrip.objects.get(trip_request_id=trip_id)
            print("trip object got")
        except TblTrip.DoesNotExist:
            return Response({'error': f'Trip {trip_id} Not Found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Render notification HTML templates
            emp_notification_data = get_template('emp_note.html').render({'trip': trip})
            driver_notification_data = get_template('driver_note.html').render({'trip': trip})
            driver_notification_message = (
                f"Trip ID: {trip.trip_request_id}\n"
                f"Passenger Name: {trip.trip_passengers.first().passenger.passenger_name}\n"
                f"Passenger Contact: {trip.trip_passengers.first().passenger.passenger_contact_number}\n"
                f"Location: {trip.trip_passengers.first().pickup_location}\n"
                f"Trip Time: {trip.trip_time.strftime('%d-%m-%Y %H:%M')}\n\n"
                f"<button onclick=\"window.location.href='http://yourapp.com/driver_trip_view?trip_id={trip.trip_request_id}'\">View Details</button>"
            )
            print("emp,driver template data prepared")
        except TemplateDoesNotExist as e:
            return Response({'error': f'Template does not exist: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Collect user IDs for notifications
        emp_user_ids = []
        for emp in trip.trip_passengers.all():
            try:
                passenger = TblPassenger.objects.get(passenger_id=emp.passenger.passenger_id)
                user = User.objects.get(username=passenger.user_id) # if users have same names that will be a fix()
                emp_user_ids.append(user.id)
            except TblPassenger.DoesNotExist as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except User.DoesNotExist as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        driver_user_id = []
        try:
            driver = TblDriver.objects.get(driver_id=trip.driver.driver_id)
            driver_user_id.append(driver.user.id)
        except TblDriver.DoesNotExist as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"emp_ids:{emp_user_ids}, driver_id:{driver_user_id}")

        # Send notifications
        try:
            notify_emps = send_notification(emp_user_ids, emp_notification_data)
            notify_driver = send_notification(driver_user_id, driver_notification_message)
            print("notification sent to users")
            return Response({'success': True, 'notify_emps':notify_emps, 'notify_driver':notify_driver}, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle any other exceptions that may occur during notification sending
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
