# -*- coding: utf8 -*-
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404, resolve_url
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters

from models import CatUser, CatRecord
from forms import AddRecordForm


@login_required(login_url='/accounts/login/')
@csrf_exempt
def main_view(request):
    if request.method == "POST":
        if not 'owner' in request.POST or not request.POST['owner']:
            request.POST['owner'] = request.user.pk

        form = AddRecordForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = AddRecordForm()

    images = CatRecord.objects.filter(is_private=False).order_by('id')[:10]
    if len(images) % 2 == 1:
        last_image = images[len(images)-1]
    else:
        last_image = None

    images_left = images[::2]
    images_right = images[1::2]
    images_list = zip(images_left, images_right)

    context = RequestContext(request)
    context['friend_token'] = CatUser.objects.get(pk=request.user.pk).friend_token
    context['form'] = form
    context['images'] = images_list
    context['last_image'] = last_image
    return render_to_response('index.html', context)


@csrf_exempt
def registration(request):
    if request.method == "POST":
        data = request.POST
        user_login = data['login']
        user_password = data['password']
        if user_login and user_password:
            test_user = CatUser.objects.filter(username=user_login)
            if len(test_user):
                return HttpResponse('already existed user!')

            user = CatUser.objects.create_user(user_login, None, user_password)
            user.save()
            return redirect('/accounts/login/')
    else:
        context = RequestContext(request)
        return render_to_response('registration/register.html', context)


def render_images_list(request, images):
    if len(images) % 2 == 1:
        last_image = images[len(images)-1]
    else:
        last_image = None

    images_left = images[::2]
    images_right = images[1::2]
    images_list = zip(images_left, images_right)

    context = RequestContext(request)
    context['friend_token'] = CatUser.objects.get(pk=request.user.pk).friend_token
    context['images'] = images_list
    context['last_image'] = last_image
    return render_to_response('index.html', context)


@login_required(login_url='/accounts/login/')
@csrf_exempt
def search(request):
    fields = [x.name for x in CatRecord._meta.fields]
    data = request.GET or request.POST
    data_dict = {}
    for elem in data:
        data_dict[elem] = data[elem]

    #if not 'is_private' in data_dict:
    data_dict['is_private'] = '0'

    if 'owner' in data_dict:
        data_dict['owner'] = get_object_or_404(CatUser, username=data['owner'])

    images = CatRecord.objects.all()
    for elem in data_dict:
        if elem in fields:
            temp_dict = {elem: data_dict[elem]}
            images = images.filter(**temp_dict)

    return render_images_list(request, images)


@login_required(login_url='/accounts/login/')
def user_images(request, user_name):
    data = request.GET
    user = get_object_or_404(CatUser, username=user_name)

    is_friend = False
    if 'friend_token' in data:
        is_friend = user.friend_token == data['friend_token']

    images_list = CatRecord.objects.filter(
        owner=user)
    if user.pk != request.user.pk and not is_friend:
        images_list = images_list.filter(
            is_private=False)

    return render_images_list(request, images_list)


def users_list(request):
    context = RequestContext(request)
    context['users'] = CatUser.objects.all()
    return render_to_response('users.html', context)


# КОПИПАСТ ДЖАНГИ
@sensitive_post_parameters()
@csrf_exempt
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)