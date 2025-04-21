from django.db import migrations
from django.db import models
from django.conf import settings


class Migration(migrations.Migration):
       dependencies = [
           ('complaints', '0003_auto_20250421_1335'),  # Replace with your last migration name
       ]

       operations = [
           # Drop the title column
           migrations.RunSQL(
               sql='ALTER TABLE complaints_complaint DROP COLUMN title;',
               reverse_sql='ALTER TABLE complaints_complaint ADD COLUMN title VARCHAR(255) NOT NULL DEFAULT \'Untitled Complaint\';'
           ),
           # Make latitude, longitude, and address optional
           migrations.AlterField(
               model_name='Complaint',
               name='latitude',
               field=models.FloatField(blank=True, null=True),
           ),
           migrations.AlterField(
               model_name='Complaint',
               name='longitude',
               field=models.FloatField(blank=True, null=True),
           ),
           migrations.AlterField(
               model_name='Complaint',
               name='address',
               field=models.TextField(blank=True),
           ),
       ]