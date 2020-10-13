# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Repository(models.Model):
    repository_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    owner = models.CharField(max_length=45)
    user_user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'repository'

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    profile = models.CharField(max_length=45, blank=True, null=True)
    userlogin = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'user'

class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    period = models.CharField(max_length=45)
    attenddes = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event'
