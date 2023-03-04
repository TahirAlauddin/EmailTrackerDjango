from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from cryptography.fernet import Fernet
from PIL import Image
from .models import Recipient, AppUser
import pytracking
from random import randint

key = Fernet.generate_key()


def render_1_by_1_pixel(request, email_details):
    
    full_url = request.get_host() + '/1by1pixel/' + email_details
    
    tracking_result = pytracking.get_open_tracking_result(
        full_url, base_open_tracking_url=f"{request.get_host()}/1by1pixel/",
        encryption_bytestring_key=key,
        )
    
    recipient_id = tracking_result.metadata['recipient_id']
    email_campaign_id = tracking_result.metadata['email_campaign_id']
    sender_email_address = tracking_result.metadata['sender']

    # Make sure sender exists
    sender = AppUser.objects.filter(email_address=sender_email_address)
    if sender:
        sender = sender.first() # AppUser
    else:
        return JsonResponse({'error': 'Sender doesn\'t exist.'}, status=404)
    

    recipients = Recipient.objects.filter(recipient_id=recipient_id,
                                        email_campaign_id=email_campaign_id,
                                        sender=sender
                                        )
    if recipients:
        recipient = recipients.first()
        recipient.opened = True
        recipient.save()
    
    red = Image.new('RGBA', (1, 1), (randint(0,255),randint(0, 255),randint(0, 255),0))
    response = HttpResponse(content_type="image/png")
    red.save(response, "PNG")
    return response


def render_link_clicked(request, email_details):
    
    full_url = request.get_host() + '/link-clicked/' + email_details
    
    tracking_result = pytracking.get_open_tracking_result(
        full_url, base_open_tracking_url=f"{request.get_host()}/link-clicked/",
        encryption_bytestring_key=key,
        )
    
    recipient_id = tracking_result.metadata['recipient_id']
    email_campaign_id = tracking_result.metadata['email_campaign_id']
    sender_email_address = tracking_result.metadata['sender']
    tracked_url = tracking_result.tracked_url

    # Make sure sender exists
    sender = AppUser.objects.filter(email_address=sender_email_address)
    if sender:
        sender = sender.first() # AppUser
    else:
        return JsonResponse({'error': 'Sender doesn\'t exist.'}, status=404)
    
    recipients = Recipient.objects.filter(recipient_id=recipient_id,
            email_campaign_id=email_campaign_id,
            sender=sender
            )
    if recipients:
        recipient = recipients.first()
        recipient.clicked = True
        recipient.save()
    
    return redirect(tracked_url)


@csrf_exempt
def get_open_tracking_url(request):
    url = '1by1pixel'

    if request.method == 'POST':
        try:
            recipient_id = request.POST['recipient_id']
            email_campaign_id = request.POST['email_campaign_id']
            sender_email_address = request.POST['sender']
    
            sender= AppUser.objects.filter(email_address=sender_email_address)
            if sender:
                sender = sender.first() # AppUser
            else:
                return JsonResponse({'error': 'Sender doesn\'t exist.'}, status=404)
                

            recipient_count = Recipient.objects.filter(
                                    recipient_id=recipient_id,
                                    email_campaign_id=email_campaign_id,
                                    sender=sender,    
                                ).count()
            if recipient_count < 1:
                return JsonResponse({'error': 'Recipient doesn\'t exist. Please create a new recipient'}, status=404)

            configuration = pytracking.Configuration(
                base_open_tracking_url=f"{request.get_host()}/{url}/",
                include_webhook_url=False)
           
            tracking_url = pytracking.get_open_tracking_url(
                {"recipient_id": recipient_id, "email_campaign_id": email_campaign_id,
                 "sender": sender_email_address},
                encryption_bytestring_key=key,
                configuration=configuration)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=404)

        return JsonResponse({'url': tracking_url}, status=200)


@csrf_exempt
def get_click_tracking_url(request):
    url = 'link-clicked'
    
    if request.method == 'POST':
        try:
            recipient_id = request.POST['recipient_id']
            email_campaign_id = request.POST['email_campaign_id']
            sender_email_address = request.POST['sender']

            # The sender must exist
            sender = AppUser.objects.filter(email_address=sender_email_address)
            if sender:
                sender = sender.first() # AppUser
            else:
                return JsonResponse({'error': 'Sender doesn\'t exist.'}, status=404)
                

            configuration = pytracking.Configuration(
                base_open_tracking_url=f"{request.get_host()}/{url}/",
                include_webhook_url=False)

            recipients = Recipient.objects.filter(
                recipient_id=recipient_id,
                email_campaign_id=email_campaign_id,
                sender=sender
            )
            if len(recipients) < 1:
                return JsonResponse({'error': 'Recipient doesn\'t exist. Please create a new recipient'})
                
            recipient = recipients.first()

            if recipient.opened == True:
                return JsonResponse({'error': 'Already tracking this link!'})
            tracking_url = pytracking.get_click_tracking_url(
                request.POST['url'],
                {"recipient_id": recipient_id, 
                "email_campaign_id": email_campaign_id,
                "sender": sender_email_address},             
                encryption_bytestring_key=key,
                configuration=configuration)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=404)

        return JsonResponse({'url': tracking_url}, status=200)


def list_recipients(request):
    recipients_query = Recipient.objects.all()
    recipients = []
    try:
        for recipient in recipients_query:
            recipients.append({'email_address': recipient.email_address,
                            'email_campaign_id': recipient.email_campaign_id,
                            'recipient_id': recipient.recipient_id, 'opened': recipient.opened,
                            'first_name': recipient.first_name, 'last_name': recipient.last_name,
                            'company_name': recipient.company_name, 'clicked': recipient.clicked,
                            'sender': recipient.sender.email_address})
        return JsonResponse(recipients, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def create_recipient(request):
    if request.method == 'POST':
        try:
            recipient_id = request.POST['recipient_id']
            email_campaign_id = request.POST['email_campaign_id']
            email_address = request.POST['email_address']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            company_name = request.POST['company_name']
            sender_email_address = request.POST['sender']

            sender = AppUser.objects.filter(email_address=sender_email_address).first()

            recipient_count = Recipient.objects.filter(
                recipient_id=recipient_id,
                email_campaign_id=email_campaign_id,
                sender=sender,
                ).count()
            
            if recipient_count < 1:
                Recipient.objects.create(recipient_id=recipient_id,
                    email_campaign_id=email_campaign_id,
                    email_address=email_address,
                    first_name=first_name,
                    last_name=last_name,
                    company_name=company_name,
                    sender=sender)
                
                return JsonResponse({'message': 'Recipient Successfully created!'}, status=201)
            
            return JsonResponse({'message': 'Recipient already exists!'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
def create_app_user(request):
    if request.method == 'POST':
        try:
            user_name = request.POST['user_name']
            email_address = request.POST['email_address']
            license = request.POST['license']
            
            _, created = AppUser.objects.get_or_create(user_name=user_name, 
                                                        email_address=email_address,
                                                        license=license)

            if created:
                return JsonResponse({'message': 'User Successfully created!'}, status=201)
            return JsonResponse({'message': 'User already exists!'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({"error": "Not allowed"}, status=405)
    

def get_analytics_of_email(request, sender, email_campaign_id,):
    recipients = Recipient.objects.filter(email_campaign_id=email_campaign_id,
                                          sender=sender)

    try:
        opened = clicks = 0
        if len(recipients) >=1 :
            for recipient in recipients:
                if recipient.clicked:
                    clicks += 1
                if recipient.opened:
                    opened += 1

            return JsonResponse({'opened': opened, 'clicks': clicks}, status=200)
        return JsonResponse({'message': 'No recipient found in this campaign'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def handle_authorization_code(request):
    authorization_code = request.GET['code']
    print(authorization_code)
    return HttpResponse("You are all set! You can close the browser now!")


def list_app_users(request):
    app_users_query = AppUser.objects.all()
    appUsers = []
    try:
        for appUser in app_users_query:
            appUsers.append({'email_address': appUser.email_address,
                            'user_name': appUser.user_name,
                            'license': appUser.license
                            })
        return JsonResponse(appUsers, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

