from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post
from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib import messages

import facebook as fb


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('main')


class RegisterPage(FormView):
    template_name = "base/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("main")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class Main(LoginRequiredMixin, CreateView):
    model = Post
    fields = "__all__"
    template_name = "base/main.html"
    success_url = reverse_lazy("main")

    def post(self, request, *args, **kwargs):
        text1 = request.POST.get('text')
        user = self.request.user

        try:
            social_account = SocialAccount.objects.get(user=user, provider='facebook')
            tokens = SocialToken.objects.filter(account=social_account, account__provider='facebook')
            if tokens.exists():
                token = tokens.order_by('-expires_at').first()
                user_access_token = token.token

                # Initialize the Facebook Graph API with the user access token
                graph_api = fb.GraphAPI(user_access_token)

                # Get the pages the user manages
                pages_data = graph_api.get_object('me/accounts')
                pages = pages_data.get('data', [])

                if pages:
                    # Assuming you want to use the first page in the list
                    page_access_token = pages[0].get('access_token')
                    page_id = pages[0].get('id')
                    page_name = pages[0].get('name')

                    if page_access_token:
                        print(f"Page Access Token for {page_name}: {page_access_token}")

                        # Initialize the Facebook Graph API with the page access token
                        page_graph_api = fb.GraphAPI(page_access_token)

                        # Post the message to the page's feed
                        page_graph_api.put_object(page_id, "feed", message=text1)
                        messages.success(request, "Success, Check your page")
                    else:
                        print("No page access token found")
                else:
                    print("No pages found for the user")

            else:
                print("No social token found")
        except SocialAccount.DoesNotExist:
            print("No social account linked")

        return super().post(request, *args, **kwargs)
