# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals


from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserSignupDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.CharField(max_length=120, blank=True, null=True)
    country_id = models.IntegerField(blank=True, null=True)
    role = models.IntegerField(blank=True, null=True)
    title = models.IntegerField(blank=True, null=True)
    dr_licence = models.CharField(max_length=25, blank=True, null=True)
    ph_licence = models.CharField(max_length=25, blank=True, null=True)

    # class Meta:
    #     unique_together = ('dr_licence', 'ph_licence')

class PatientData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    contact_number = models.BigIntegerField(null=False)


class PaypalTransaction(models.Model):
    SUBSCRIPTION_CHOICES = (
        ('1-20', '1-20'),
        ('21-50', '21-50'),
        ('51-100', '51-100')
    )
    TRANSACTION_STATUS = (
        ('NONE', 'NONE'),
        ('SUCCESS', 'SUCCESS'),
        ('PENDING', 'PENDING'),
        ('REFUND', 'REFUND'),
        ('CANCELLED', 'CANCELLED')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_type = models.CharField(choices=SUBSCRIPTION_CHOICES, default='1-20', max_length=10)
    amount = models.IntegerField()
    transaction_no=models.CharField(default='none', max_length=30)
    transaction_date = models.DateTimeField(default=datetime.now())
    transaction_status = models.CharField(choices=TRANSACTION_STATUS, default='NONE', max_length=15)

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserSignupDetails.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

# class User(models.Model):
#     user_id = models.OneToOneField('User', primary_key=True)
#     firstname = models.CharField(max_length=45, blank=True, null=True)
#     lastname = models.CharField(max_length=45, blank=True, null=True)
#     user_password = models.TextField()
#     use_db = models.IntegerField(blank=True, null=True)
#     last_login = models.DateTimeField(auto_now_add=True, blank=True)
#     share_data = models.BooleanField()  # This field type is a guess.
#     email_address = models.CharField(max_length=250)
#     paid = models.BooleanField()  # This field type is a guess.
#     account_paid_date = models.DateTimeField(blank=True, null=True)
#     initial_device = models.CharField(max_length=10, blank=True, null=True)
#     allow_access = models.BooleanField() #This field type is a guess.
#     deny_reason = models.IntegerField(blank=True, null=True)
#     date_of_birth = models.DateField(blank=True, null=True)
#     gender = models.CharField(max_length=1, blank=True, null=True)
#     country_id = models.IntegerField(blank=True, null=True)
#     accept_tc = models.BooleanField()  # This field type is a guess.
#     denied_by = models.IntegerField(blank=True, null=True)
#     created_date = models.DateTimeField(blank=True, null=True)
#     last_update = models.DateTimeField(blank=True, null=True)
#     signup_completed = models.BooleanField()  # This field type is a guess.
#     push_registration = models.CharField(max_length=255, blank=True, null=True)
#     monthly_questionnaire = models.DateField(blank=True, null=True)
#     taking_ldn = models.NullBooleanField(blank=True, null=True)  # This field type is a guess.
#     push_registration_android = models.CharField(max_length=255, blank=True, null=True)
#     dr_licence = models.CharField(max_length=25, blank=True, null=True)
#     ph_licence = models.CharField(max_length=25, blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'user'
#
#
