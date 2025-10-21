from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model


from .models import Contact
from .serializers import UserSerializer

User = get_user_model()


class SubmitContactView(View):
    def post(self, request):
        contact = Contact(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        contact.save()
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')  # Redirect to your contact page


