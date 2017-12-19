# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.views.decorators.csrf import csrf_protect
from django.template.context_processors import csrf
from django.core.mail import send_mail
from .models import *


def login_view(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('loginLDN_pass.html', c)


# @csrf_protect
def email_signup_verify(request):
    if request.POST:
        form = request.POST
        username = form['username']
        password = form['password']
        dr_licence = form['dr_licence']
        ph_licence_number = form['ph_licence_number']
        website = form['website']
        country_id = form['txtCountry']
        role_id = form['txtRole']
        title_id = form['txtTitle']
        email = form['email']

        User.objects.create(username=username, email=email, is_active=False)

        user_id = User.objects.last().id
        user_obj = User.objects.get(id = user_id)
        user_obj.set_password(password)
        user_obj.save()
        UserSignupDetails.objects.create(user_id=user_id, country_id=country_id, dr_licence=dr_licence,
                                         ph_licence=ph_licence_number, website=website, title=title_id, role=role_id)

        email_body = 'Approval request received with following details:' + \
                     '\nDoctor Licence :' + dr_licence + \
                     '\nPharamacist Licence :' + ph_licence_number + \
                     '\nEmail : ' + email + \
                     '\nWebsite :' + website + \
                     '\nCountry ID :' + country_id + \
                     '\nRole :' + role_id + \
                     '\nTitle :' + title_id + \
                     '\nUsername :' + username + \
                     '\n\nKindly check admin panel for more details.'

        send_mail(
            'Approval Request',
            email_body,
            'gvoicecall31@gmail.com',
            ['gvoicecall31@gmail.com'],
            fail_silently=False,
        )
        return redirect("/ldn/login/")

    return HttpResponse("Method: /GET not allowed")  # @login_required


@login_required(login_url='/ldn/adminlogin/')
@user_passes_test(lambda u: u.is_superuser)
def admin_panel_verify(request):
    c = {}
    c.update(csrf(request))
    if request.method == "POST":
        user_obj = User.objects.get(id=int(request.POST['user_id']))
        user_obj.is_active = True
        user_obj.save()
        email_body = 'Hello ' + user_obj.username.upper() + ',\n\nWe welcome you to our family. ' \
                                                            'Your request for access to LDN research is accepted by admin. You can now login and perform your analysis.  '
        send_mail(
            'Access Confirmed',
            email_body,
            'gvoicecall31@gmail.com',
            ['gvoicecall31@gmail.com'],  # user_obj.email
            fail_silently=False,
        )

        return redirect("/ldn/adminpanel/")

    unverified_users_id = User.objects.filter(is_active=False).values_list('id', 'username','date_joined').order_by('date_joined')
    unverified_users = UserSignupDetails.objects.filter(user_id__in=[i[0] for i in unverified_users_id])
    c['unverified_users'] = zip([[i[1],i[2]] for i in unverified_users_id], unverified_users)

    return render_to_response('admin_panel.html', c)


def admin_login_verify(request):
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        u_name = request.POST['username']
        pwd = request.POST['password']

        try:
            user_obj = authenticate(request, username=u_name, password=pwd)
        except:
            return HttpResponse("Username/Password not matched")

        if user_obj is not None:
            if not user_obj.is_active:
                return HttpResponse("Your request is not approved. Please try again later.")

            login(request, user_obj)
            return HttpResponseRedirect(request.POST.get('next'))
        else:
            return HttpResponse("Invalid login please try again")
    c['next'] = request.GET.get('next', '')
    return render_to_response('adminloginLDN.html', c)


def user_login_verify(request):
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        u_name = request.POST['username']
        dr_licence = request.POST['dr_licence']
        pwd = request.POST['password']

        try:
            user_obj = User.objects.get(username=u_name, password=pwd)
        except:
            try:
                user_obj = authenticate(request, username=u_name, password=pwd)
            except:
                return HttpResponse("Username/Password not matched")

        if user_obj is not None:
            if not user_obj.is_active:
                return HttpResponse("Your request is not approved. Please try again later.")

            signin_user = UserSignupDetails.objects.get(user_id=user_obj.id)
            if signin_user.dr_licence == dr_licence:
                login(request, user_obj)
                return HttpResponseRedirect("/ldn/userpatients/")
            else:
                return HttpResponse("Wrong Dr Licence Number")
        else:
            return HttpResponse("Invalid login please try again")


def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/ldn/login/")


def send_password(request):
    if request.method == 'POST':
        try:
            user_obj = User.objects.get(username__exact= request.POST.get('username',''))
        except:
            # try:
            #     user_obj = UserSignupDetails.objects.get(dr_licence__exact=request.POST.get('username', ''))
            # except:
            #     return HttpResponse("Enter correct username")
            return HttpResponse("Enter correct username")

        if user_obj is not None:
            if not user_obj.is_active:
                return HttpResponse("Your request is not approved. Please try again later.")
            chars = string.ascii_uppercase + string.digits
            new_pass = ''.join(random.choice(chars) for _ in range(6))
            user_obj.set_password(new_pass)
            user_obj.save()
            email_body = 'Hello '+user_obj.username.upper()+',\n\n Your password is reset to '+new_pass+'.\nPlease login to continue.'
            send_mail(
                'Password Reset',
                email_body,
                'gvoicecall31@gmail.com',
                ['gvoicecall31@gmail.com'], #user_obj.email
                fail_silently=False,
            )

        return HttpResponseRedirect("/ldn/login/")

    return HttpResponseRedirect("/ldn/login/")


@login_required(login_url='/ldn/login/')
def user_patients(request):
    patient_data = PatientData.objects.filter(user_id=request.user.id)
    c = {}
    c['patient_data'] = patient_data
    return render_to_response('patient_data.html', c)
