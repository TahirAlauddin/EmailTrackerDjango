# Generated by Django 4.1.6 on 2023-02-15 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_address', models.EmailField(max_length=255)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('recipient_id', models.IntegerField()),
                ('recipient_list_id', models.IntegerField()),
                ('email_campaign_id', models.IntegerField()),
                ('status', models.BooleanField(default=False)),
                ('clicked', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddConstraint(
            model_name='recipient',
            constraint=models.UniqueConstraint(fields=('recipient_id', 'recipient_list_id', 'email_campaign_id'), name='unique_recipient_per_campaign'),
        ),
    ]