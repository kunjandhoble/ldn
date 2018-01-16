# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string, json
#
# import json as json
import time
import paypalrestsdk
from MySQLdb import escape_string as thwart
from decimal import Decimal

from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.urls import reverse
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests
import braintree
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.views.decorators.csrf import csrf_protect
from django.template.context_processors import csrf
from django.core.mail import send_mail
from django.contrib import messages
from .models import *
from .dashboard_data import *


def login_view(request):
    c = {}
    c.update(csrf(request))
    for msg in messages.get_messages(request):
        c["message"] = msg
        # print(msg)
    return render_to_response('loginLDNewHarshal.html', c)


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
        user_obj = User.objects.get(id=user_id)
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

    unverified_users_id = User.objects.filter(is_active=False).values_list('id', 'username', 'date_joined').order_by(
        'date_joined')
    unverified_users = UserSignupDetails.objects.filter(user_id__in=[i[0] for i in unverified_users_id])
    c['unverified_users'] = zip([[i[1], i[2]] for i in unverified_users_id], unverified_users)

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
            # return HttpResponse("Username/Password not matched")
            messages.add_message(request, messages.INFO, "Username/Password not matched")
            return HttpResponseRedirect("/ldn/adminlogin/")

        if user_obj is not None:
            if not user_obj.is_active:
                # return HttpResponse("Your request is not approved. Please try again later.")
                messages.add_message(request, messages.INFO, "Your request is not approved. Please try again later.")
                return HttpResponseRedirect("/ldn/adminlogin/")

            login(request, user_obj)
            return HttpResponseRedirect('/ldn/adminpanel/')
        else:
            # return HttpResponse("Invalid login please try again")
            messages.add_message(request, messages.INFO, "Invalid login please try again")
            return HttpResponseRedirect("/ldn/adminlogin/")
    c['next'] = request.GET.get('next', '')
    for msg in messages.get_messages(request):
        c["message"] = msg
        # print(msg)
    return render_to_response('adminloginLDN.html', c)


def email_isunique(request):
    if User.objects.filter(email__iexact=request.POST['email']):
        return False
    return True


def user_login_verify(request):
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        email = request.POST['email']
        # licencetype = request.POST['licencetype']
        # licence = request.POST['licence']
        pwd = request.POST['password']
        err = {}
        try:
            user_obj = User.objects.get(email=email, password=pwd)
            print(user_obj,"get")
        except:
            try:
                username = User.objects.get(email__exact=email).username
                user_obj = authenticate(request, username=username, password=pwd)
            except:
                # return HttpResponse("Username/Password not matched")
                messages.add_message(request, messages.INFO, "Username/Password not matched")
                return HttpResponseRedirect("/ldn/login/")

        if user_obj is not None:
            if not user_obj.is_active:
                # return HttpResponse("Your request is not approved. Please try again later.")
                messages.add_message(request, messages.INFO, "Your request is not approved. Please try again later.")
                return HttpResponseRedirect("/ldn/login/")

            login(request, user_obj)
            return HttpResponseRedirect("/ldn/dashboard/")
            # signin_user = UserSignupDetails.objects.get(user_id=user_obj.id)
            # if licencetype == '2' and signin_user.ph_licence == licence:
            #     login(request, user_obj)
            #     return HttpResponseRedirect("/ldn/dashboard/")
            #
            # elif licencetype == '3' and signin_user.dr_licence == licence:
            #     login(request, user_obj)
            #     return HttpResponseRedirect("/ldn/dashboard/")
            #
            # else:
            #     # return HttpResponse("Wrong Dr Licence Number")
            #     messages.add_message(request, messages.INFO, "Wrong Licence Number")
            #     return HttpResponseRedirect("/ldn/login/")
        else:
            # return HttpResponse("Invalid login please try again")
            messages.add_message(request, messages.INFO, "Invalid login please try again")
            return HttpResponseRedirect("/ldn/login/")


def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/ldn/login/")


def send_password(request):
    if request.method == 'POST':
        try:
            print(request.POST.get('email'))
            filtered_users = User.objects.filter(email__exact=request.POST.get('email', ''))
            print(filtered_users)
        except:
            err = {}
            # try:
            #     user_obj = UserSignupDetails.objects.get(dr_licence__exact=request.POST.get('username', ''))
            # except:
            #     return HttpResponse("Enter correct username")
            # return HttpResponse("Enter correct username")
            err["error"] = "Email does not exists"
            return render_to_response("404.html", err)

        # licence = UserSignupDetails.objects.get(user=user_obj)
        found = False
        user = ''
        if filtered_users is not None:
            for user_obj in filtered_users:
                print(user_obj.id)
                try:
                    licence = UserSignupDetails.objects.get(user_id=user_obj.id)
                except:
                    continue
                if not user_obj.is_active:
                    found = False
                    continue
                elif licence.dr_licence == request.POST.get('DR/PHLicence',
                                                            '') or licence.ph_licence == request.POST.get(
                        'DR/PHLicence', ''):
                    found = True
                    user = user_obj
                else:
                    found = False

            if not found:
                err = {}
                err["error"] = "DR/PH Licence not found or it does not match with Email"
                return render_to_response("404.html", err)

            # licence = UserSignupDetails.objects.get(user=user)
            chars = string.ascii_uppercase + string.digits
            new_pass = ''.join(random.choice(chars) for _ in range(6))
            user.set_password(new_pass)
            user.save()
            email_body = 'Hello ' + user.username + ',\n\n Your password is reset to \n\n\t\t' + new_pass + '\n\nPlease login to continue.'
            send_mail(
                'Password Reset',
                email_body,
                'gvoicecall31@gmail.com',
                ['gvoicecall31@gmail.com'],  # user_obj.email
                fail_silently=False,
            )

        return HttpResponseRedirect("/ldn/login/")

    return HttpResponseRedirect("/ldn/login/")


@login_required(login_url='/ldn/login/')
def changepassword(request):
    c = {}
    c.update(csrf(request))
    if request.method == "POST":
        user_id = request.user.id
        old_pwd = request.POST.get('current_pwd', '')
        new_pwd = request.POST.get('new_pwd', '')
        confirm_pwd = request.POST.get('confirm_pwd', '')
        test_passed = True
        user = User.objects.get(id=user_id)
        if old_pwd == new_pwd:
            messages.add_message(request, messages.ERROR, "Current and New Password must be different")
            test_passed = False
        if not user.check_password(str(old_pwd)):
            messages.add_message(request, messages.ERROR, "Incorrect Old Password")
            test_passed = False
        if new_pwd != confirm_pwd:
            messages.add_message(request, messages.ERROR, "New Passwords do not match")
            test_passed = False
        if new_pwd == '' or confirm_pwd == '' or old_pwd == '':
            messages.add_message(request, messages.ERROR, "Blank Password field not allowed")
            test_passed = False
        if test_passed:
            try:
                user.set_password(str(new_pwd))
                user.save()
            except:
                messages.add_message(request, messages.ERROR, "Some error occurred. Please try after some time.")
                test_passed = False
        return HttpResponseRedirect("/ldn/changepassword/")
    for msg in messages.get_messages(request):
        print(msg)
        c["message"] = msg
    return render_to_response('registration/password_reset_confirm.html', c)


@login_required(login_url='/ldn/login/')
def user_patients(request):
    try:
        user_id = PaypalTransaction.objects.get(user_id=request.user.id)
    except:
        return HttpResponseRedirect('/ldn/purchase/')

    if user_id.transaction_status != 'COMPLETED':
        return HttpResponseRedirect('/ldn/purchase/')
    else:
        patient_data = PatientData.objects.filter(user_id=request.user.id)
        c = {}
        c.update(csrf(request))
        c['patient_data'] = patient_data
        c.update({'NA': 'Invalid patient id. Please try again.'})
        c.update({'request': request})
        return render_to_response('patientdata.html', c)


# @login_required(login_url='/ldn/login/')
# def graphs(request, tablename, userid):
#     if tablename == 'oswestry':
#         dc = oswestry_data(tablename, userid)
#         return render_to_response('dashboard/oswestry.html', dc)
#     elif tablename == 'cdc':
#         dc = cdc_data(tablename, userid)
#         return render_to_response('dashboard/cdc.html', dc)
#     elif tablename == 'weight':
#         dc = weight_data(tablename, userid)
#         return render_to_response('dashboard/weight.html', dc)
#     elif tablename == 'prescriptionmeds':
#         dc = prescriptionmeds_data('prescription_meds',userid)
#         return render_to_response('dashboard/prescriptionmeds.html', dc)
#     elif tablename == 'pain':
#         dc = pain_data('pain_tracker', userid)
#         return render_to_response('dashboard/pain_tracker.html', dc)
#     elif tablename == 'dosehistory':
#         dc = dosehistory_data('research_dose_history', userid)
#         return render_to_response('dashboard/dose_history.html', dc)
#     elif tablename == 'sleep':
#         dc = sleep_data(tablename, userid)
#         return render_to_response('dashboard/sleep.html', dc)
#     elif tablename == 'cfsfibrotracker':
#         dc = cfsfibrotracker_data('cfs_fibro_tracker', userid)
#         return render_to_response('dashboard/cfs_fibrotracker.html', dc)
#     elif tablename == 'myday':
#         dc = myday_data(tablename, userid)
#         return render_to_response('dashboard/myday.html', dc)
#     elif tablename == 'currentdose':
#         dc = currentdose_data(tablename, userid)
#         return render_to_response('dashboard/currentdose.html', dc)
#     elif tablename == 'ldntracker':
#         dc = ldntracker_data(tablename, userid)
#         return render_to_response('dashboard/ldntracker.html', dc)
#     else:
#         dc = {}
#     return render_to_response('dashboard/DashSecond.html', dc)

@login_required(login_url='/ldn/login/')
def graphs(request, patientid):
    startdate = request.GET.get('start', '')
    enddate = request.GET.get('end', '')

    doctor = UserSignupDetails.objects.get(user_id=int(request.user.id))
    sqlquery = r'SELECT user_id FROM ldnappor_development.user'
    if doctor.dr_licence is not None or doctor.dr_licence is not '':
        sqlquery += r' where dr_licence = "{0}"'.format(doctor.dr_licence)
    if doctor.ph_licence is not None or doctor.ph_licence is not '':
        sqlquery += r' or ph_licence = "{0}"'.format(doctor.ph_licence)
    data = fetch_data_from_db(sqlquery=sqlquery)

    # check patient id in subscription id list from user table.
    dc = {}
    dc.update(csrf(request))
    if patientid not in [str(row[0]) for row in data]:
        doctor = UserSignupDetails.objects.get(user_id=int(request.user.id))
        sqlquery = r'SELECT user_id, CONCAT(firstname,lastname) as fullname FROM ldnappor_development.user'
        if doctor.dr_licence is not None or doctor.dr_licence is not '':
            sqlquery += r' where dr_licence = "{0}"'.format(doctor.dr_licence)
        if doctor.ph_licence is not None or doctor.ph_licence is not '':
            sqlquery += r' or ph_licence = "{0}"'.format(doctor.ph_licence)
        data = fetch_data_from_db(sqlquery=sqlquery)
        patient_data = []
        for row in data:
            patient_data.append((row[0], row[1]))
        # patient_data = PatientData.objects.filter(user_id=request.user.id)
        c = {}
        c.update(csrf(request))
        c['patient_data'] = patient_data
        c['NA'] = "Patient Id = {} not found. Try again with a different id.".format(patientid)
        c.update({'request': request})
        return render_to_response('patientdata.html', c)

    dc.update({'request': request})
    sqlquery = r'SELECT user_id, CONCAT(firstname,lastname) FROM ldnappor_development.user where user_id={0}'.format(
        patientid)
    data = fetch_data_from_db(sqlquery=sqlquery)
    dc.update({'patient_data': (data[0][0], data[0][1])})
    dc.update(oswestry_data('oswestry', patientid, startdate, enddate))
    dc.update(cdc_data('cdc', patientid, startdate, enddate))
    dc.update(weight_data('weight', patientid, startdate, enddate))
    dc.update(prescriptionmeds_data('prescription_meds', patientid, startdate, enddate))
    dc.update(pain_data('pain_tracker', patientid, startdate, enddate))
    dc.update(dosehistory_data('research_dose_history', patientid, startdate, enddate))
    dc.update(sleep_data('sleep', patientid, startdate, enddate))
    dc.update(cfsfibrotracker_data('cfs_fibro_tracker', patientid, startdate, enddate))
    dc.update(myday_data('myday', patientid, startdate, enddate))
    dc.update(currentdose_data('currentdose', patientid, startdate, enddate))
    dc.update(ldntracker_data('ldntracker', patientid, startdate, enddate))
    # dc.update(alcoholtracker_data('alcoholtracker', patientid, startdate, enddate))

    return render_to_response('dashboard.html', dc)


@login_required(login_url='/ldn/login/')
def dashboard(request):
    if request.method == "POST":
        patient_id = request.POST.get('patient_id')
        try:
            doctor = UserSignupDetails.objects.get(user_id=int(request.user.id))
            sqlquery = r'SELECT user_id FROM ldnappor_development.user'
            if doctor.dr_licence is not None or doctor.dr_licence is not '':
                sqlquery += r' where dr_licence = "{0}"'.format(doctor.dr_licence)
            if doctor.ph_licence is not None or doctor.ph_licence is not '':
                sqlquery += r' or ph_licence = "{0}"'.format(doctor.ph_licence)
            data = fetch_data_from_db(sqlquery=sqlquery)

            # doctor_id = '1712' #doctor.id
            if doctor.user.is_active and patient_id in [str(row[0]) for row in data]:
                return HttpResponseRedirect('/ldn/graphs/' + patient_id)
            else:
                doctor = UserSignupDetails.objects.get(user_id=int(request.user.id))
                sqlquery = r'SELECT user_id, CONCAT(firstname,lastname) as fullname FROM ldnappor_development.user'
                if doctor.dr_licence is not None or doctor.dr_licence is not '':
                    sqlquery += r' where dr_licence = "{0}"'.format(doctor.dr_licence)
                if doctor.ph_licence is not None or doctor.ph_licence is not '':
                    sqlquery += r' or ph_licence = "{0}"'.format(doctor.ph_licence)
                data = fetch_data_from_db(sqlquery=sqlquery)
                patient_data = []
                for row in data:
                    patient_data.append((row[0], row[1]))
                # patient_data = PatientData.objects.filter(user_id=request.user.id)
                c = {}
                c.update(csrf(request))
                c['patient_data'] = patient_data
                c.update({'NA': 'no record found'})
                c.update({'request': request})
                return render_to_response('patientdata.html', c)
        except:
            doctor = UserSignupDetails.objects.get(user_id=int(request.user.id))
            sqlquery = r'SELECT user_id, CONCAT(firstname,lastname) as fullname FROM ldnappor_development.user'
            if doctor.dr_licence is not None or doctor.dr_licence is not '':
                sqlquery += r' where dr_licence = "{0}"'.format(doctor.dr_licence)
            if doctor.ph_licence is not None or doctor.ph_licence is not '':
                sqlquery += r' or ph_licence = "{0}"'.format(doctor.ph_licence)
            data = fetch_data_from_db(sqlquery=sqlquery)
            patient_data = []
            for row in data:
                patient_data.append((row[0], row[1]))
            # patient_data = PatientData.objects.filter(user_id=request.user.id)
            c = {}
            c.update(csrf(request))
            c['patient_data'] = patient_data
            c.update({'NA': 'Invalid patient id. Please try again.'})
            c.update({'request': request})
            return render_to_response('patientdata.html', c)
    else:
        try:
            user_id = PaypalTransaction.objects.get(user_id=request.user.id)
        except:
            return HttpResponseRedirect('/ldn/purchase/')

        if user_id.transaction_status != 'COMPLETED':
            return HttpResponseRedirect('/ldn/purchase/')
        else:

            doctor = UserSignupDetails.objects.get(user_id=int(request.user.id))
            sqlquery = r'SELECT user_id, CONCAT(firstname,lastname) as fullname FROM ldnappor_development.user'
            if doctor.dr_licence is not None or doctor.dr_licence is not '':
                sqlquery += r' where dr_licence = "{0}"'.format(doctor.dr_licence)
            if doctor.ph_licence is not None or doctor.ph_licence is not '':
                sqlquery += r' or ph_licence = "{0}"'.format(doctor.ph_licence)
            data = fetch_data_from_db(sqlquery=sqlquery)
            patient_data = []
            for row in data:
                patient_data.append((row[0], row[1]))
            # patient_data = PatientData.objects.filter(user_id=request.user.id)
            c = {}
            c.update(csrf(request))
            c['patient_data'] = patient_data
            c.update({'request': request})
            return render_to_response('patientdata.html', c)


def client_token():
    return braintree.ClientToken.generate()


def create_purchase(request):
    if request.method == "GET":
        c = {}
        c.update(csrf(request))
        c['client_token'] = json.dumps(client_token())
        return render_to_response('paypalform.html', c)
    else:
        # print(request.POST)
        nonce_from_the_client = request.POST.get("payment_method_nonce")
        # print(nonce_from_the_client)
        result = braintree.Transaction.sale({
            "amount": "10.00",
            "payment_method_nonce": nonce_from_the_client,
            "options": {
                "submit_for_settlement": True
            }
        })
        settled_transaction = ''
        if result.is_success:
            print(result.transaction)
            settled_transaction = result.transaction

        else:
            print(result.errors.errors.data)
        # Use payment method nonce here...
        tr_id = settled_transaction.id
        print(tr_id)
        print(json.dumps(settled_transaction))
        result = braintree.Transaction.submit_for_settlement(tr_id)

        if result.is_success:
            settled_transaction = result.transaction
            print(settled_transaction)
        else:
            print(result.errors)
        return HttpResponseRedirect('/ldn/checkout/')


@login_required(login_url='/ldn/login/')
def purchase(request):
    try:
        c = {}
        c.update(csrf(request))
        return render_to_response("paypalsuccess.html", c)

        # return render_to_response("paypalform.html")
    except Exception as e:
        return str(e)


ACCESS_TOKEN = ''


def api_access_token():
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
    }

    data = [
        ('grant_type', 'client_credentials'),
    ]
    paypal_creds = fetch_paypal_details()
    client_id = paypal_creds[0],
    client_secret = paypal_creds[1]

    response = requests.post('https://api.sandbox.paypal.com/v1/oauth2/token', headers=headers, data=data,
                             auth=(client_id, client_secret))
    ACCESS_TOKEN = response.json()['access_token']
    return ACCESS_TOKEN


@login_required(login_url='/ldn/login/')
def checkpayment(request):
    if request.is_ajax() and request.POST:
        paypal_creds = fetch_paypal_details()
        # paypal_prod_creds = fetch_paypal_prod_details()
        my_api = paypalrestsdk.Api({
            'mode': 'sandbox',
            # 'mode': 'production',
            'client_id': paypal_creds[0],
            'client_secret': paypal_creds[1]})
        payment = paypalrestsdk.Payment.find(request.POST.get('paymentID'), api=my_api)

        # PayerID is required to approve the payment.
        if [payment['intent'], payment['state']] == ['sale', 'created']:
            if [payment['transactions'][0]['amount']['currency'], payment['transactions'][0]['amount']['total']] != [
                'GBP', '300.00']:
                c = {}
                c.update(csrf(request))
                c.update({"error": "Payment Unsuccesful. Please try again and pay the subscribed amount."})
                # return render_to_response("paypalsuccess.html", c)
                return JsonResponse({"error": "payment failed"})
            else:
                print("inside else")
                if payment.execute({"payer_id": request.POST.get('payerID')}):  # return True or False
                    user = User.objects.get(id=request.user.id)
                    paypal_obj = PaypalTransaction.objects.create(user=user, subscription_type='UNLIMITED',
                                                                  amount=Decimal(
                                                                      payment['transactions'][0]['amount']['total']),
                                                                  transaction_no=request.POST.get('paymentID'),
                                                                  transaction_status='COMPLETED')
                    paypal_obj.save()
                    return JsonResponse({"success": "payment done", "url": str(reverse("dashboard"))})
                else:
                    print(payment.error)
                    return JsonResponse({"error": "payment failed"})
    else:
        c = {}
        c.update(csrf(request))
        return render_to_response("paypalsuccess.html", c)


def handler404(request):
    response = render_to_response('404.html')
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html')
    response.status_code = 500
    return response
