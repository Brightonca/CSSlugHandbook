from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import PDFUploadForm
from .models import UploadedPDF
from PyPDF2 import PdfReader  # or fitz from PyMuPDF if you prefer
import os
from django.http import JsonResponse


# Create your views here.

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            # Create and save model instance
            pdf_instance = UploadedPDF.objects.create(file=uploaded_file)

            # Get the path to the uploaded file
            file_path = pdf_instance.file.path

            # Read the PDF
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            # Optional: Store the extracted text in the model (you can add a `text` field for this)
            # pdf_instance.extracted_text = text
            # pdf_instance.save()

            return redirect('main')
    else:
        form = PDFUploadForm()

    return render(request, 'slug_quest/upload_pdf.html', {'form': form})

@csrf_exempt
def sign_in_callback(request):
    import logging
    logger = logging.getLogger(__name__)
    
    # Log incoming request data for debugging
    logger.error(f"Request method: {request.method}")
    logger.error(f"Request POST: {request.POST}")
    
    token = request.POST.get('credential')
    if not token:
        logger.error("No credential token received")
        return HttpResponse("No credential token received", status=400)
    
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            "999403221130-9nfc38cqh2q191tmldkbakab54uahokj.apps.googleusercontent.com"
        )
        
        # Log success
        logger.error(f"Successfully verified token for: {idinfo.get('email')}")
        
        # Store in session
        request.session['user_data'] = {
            'email': idinfo.get('email'),
            'given_name': idinfo.get('given_name', 'User'),
            'picture': idinfo.get('picture', '')
        }
        
        return HttpResponse("Login successful")
    except ValueError as e:
        # Invalid token
        logger.error(f"Token validation failed: {str(e)}")
        return HttpResponse(f"Invalid token: {str(e)}", status=400)
    except Exception as e:
        # Other errors
        logger.error(f"Error during login: {str(e)}")
        return HttpResponse(f"Login error: {str(e)}", status=500)

def home(request):
    return render(request, 'slug_quest/home.html')

def login_page(request):
    return render(request, 'slug_quest/login.html')

def main(request):
    return render(request, 'slug_quest/main.html')

def dashboard(request):
    # Check if user is logged in
    if 'user_data' not in request.session:
        return redirect('home')
    
    # Get user data from session
    user_data = request.session.get('user_data', {})
    
    # Log debugging info
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Dashboard accessed with user data: {user_data}")
    
    return render(request, 'slug_quest/dashboard.html', {'user_data': user_data})