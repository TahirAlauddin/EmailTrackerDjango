from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from cryptography.fernet import Fernet
from PIL import Image
from .models import Recipient
import pytracking
from random import randint


key = Fernet.generate_key()


def render_1_by_1_pixel(request, email_details):
    
    full_url = request.get_host() + '/1by1pixel/' + email_details
    
    tracking_result = pytracking.get_open_tracking_result(
        full_url, base_open_tracking_url=f"{request.get_host()}/1by1pixel/",
        # encryption_bytestring_key=key,
        )
    
    recipient_id = tracking_result.metadata['recipient_id']
    email_campaign_id = tracking_result.metadata['email_campaign_id']
    recipient_list_id = tracking_result.metadata['recipient_list_id']

    recipients = Recipient.objects.filter(recipient_id=recipient_id,
                                        email_campaign_id=email_campaign_id,
                                        recipient_list_id=recipient_list_id,
                                        )
    if recipients:
        recipient = recipients.first()
        recipient.status = True
        recipient.save()
    
    red = Image.new('RGBA', (randint(1, 50), randint(1, 50)), (randint(0,255),randint(0, 255),randint(0, 255),0))
    response = HttpResponse(content_type="image/png")
    red.save(response, "PNG")
    return response


def render_link_clicked(request, email_details):
    
    full_url = request.get_host() + '/link-clicked/' + email_details
    
    tracking_result = pytracking.get_open_tracking_result(
        full_url, base_open_tracking_url=f"{request.get_host()}/link-clicked/",
        # encryption_bytestring_key=key,
        )
    
    recipient_id = tracking_result.metadata['recipient_id']
    email_campaign_id = tracking_result.metadata['email_campaign_id']
    recipient_list_id = tracking_result.metadata['recipient_list_id']
    tracked_url = tracking_result.tracked_url

    recipients = Recipient.objects.filter(recipient_id=recipient_id,
                            email_campaign_id=email_campaign_id,
                            recipient_list_id=recipient_list_id,
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
            recipient_list_id = request.POST['recipient_list_id']
            
            recipient_count = Recipient.objects.filter(
                                    recipient_id=recipient_id,
                                    email_campaign_id=email_campaign_id,
                                    recipient_list_id=recipient_list_id,      
                                ).count()
            if recipient_count < 1:
                return JsonResponse({'error': 'Recipient doesn\'t exist. Please create a new recipient'})
            

            configuration = pytracking.Configuration(
                base_open_tracking_url=f"{request.get_host()}/{url}/",
                include_webhook_url=False)
           
            tracking_url = pytracking.get_open_tracking_url(
                {"recipient_id": recipient_id, "email_campaign_id": email_campaign_id,
                "recipient_list_id": recipient_list_id},             
                # encryption_bytestring_key=key,
                configuration=configuration)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=404)

        return JsonResponse({'url': tracking_url})


@csrf_exempt
def get_click_tracking_url(request):
    url = 'link-clicked'
    
    if request.method == 'POST':
        try:
            recipient_id = request.POST['recipient_id']
            email_campaign_id = request.POST['email_campaign_id']
            recipient_list_id = request.POST['recipient_list_id']
            configuration = pytracking.Configuration(
                base_open_tracking_url=f"{request.get_host()}/{url}/",
                include_webhook_url=False)

            recipients = Recipient.objects.filter(
                recipient_id=recipient_id,
                email_campaign_id=email_campaign_id,
                recipient_list_id=recipient_list_id,      
            )
            if len(recipients) < 1:
                return JsonResponse({'error': 'Recipient doesn\'t exist. Please create a new recipient'})
                
            recipient = recipients.first()

            if recipient.status == True:
                return JsonResponse({'error': 'Already tracking this link!'})
            tracking_url = pytracking.get_click_tracking_url(
                request.POST['url'],
                {"recipient_id": recipient_id, 
                "email_campaign_id": email_campaign_id,
                "recipient_list_id": recipient_list_id},             
                # encryption_bytestring_key=key,
                configuration=configuration)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=404)

        return JsonResponse({'url': tracking_url})



def list_recipients(request):
    recipients_query = Recipient.objects.all()
    recipients = []
    for recipient in recipients_query:
        recipients.append({'email_address': recipient.email_address, 'email_campaign_id': recipient.email_campaign_id,
                        'recipient_id': recipient.recipient_id, 'recipient_list_id': recipient.recipient_list_id,
                        'status': recipient.status, 'first_name': recipient.first_name, 'last_name': recipient.last_name,
                        'company_name': recipient.company_name, 'clicked': recipient.clicked})
    return JsonResponse(recipients, safe=False)


@csrf_exempt
def create_recipient(request):
    if request.method == 'POST':

        recipient_id = request.POST['recipient_id']
        email_campaign_id = request.POST['email_campaign_id']
        recipient_list_id = request.POST['recipient_list_id']
        email_address = request.POST['email_address']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        company_name = request.POST['company_name']

        recipient_count = Recipient.objects.filter(recipient_id=recipient_id,
                    email_campaign_id=email_campaign_id,
                    recipient_list_id=recipient_list_id).count()
        
        if recipient_count < 1:
            Recipient(recipient_id=recipient_id,
                email_campaign_id=email_campaign_id,
                recipient_list_id=recipient_list_id,
                email_address=email_address,
                first_name=first_name,
                last_name=last_name,
                company_name=company_name).save()
        
            return JsonResponse({'message': 'Recipient Successfully created!'}, status=201)
        
        return JsonResponse({'message': 'Recipient already exists!'}, status=404)
    

def get_analytics_of_email(request, email_campaign_id):
    recipients = Recipient.objects.filter(email_campaign_id=email_campaign_id)

    opened = clicks = 0
    if len(recipients) >=1 :
        for recipient in recipients:
            if recipient.clicked:
                clicks += 1
            if recipient.opened:
                opened += 1

        return JsonResponse({'opened': opened, 'clicks': clicks}, status=200)
    return JsonResponse({'message': 'No recipient found in this campaign'}, status=404)

