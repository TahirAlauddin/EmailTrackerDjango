# Generated by Django 4.1.6 on 2023-03-01 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=254, null=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=254, null=True, verbose_name='last name')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('license', models.CharField(max_length=12, verbose_name='License Key')),
                ('email_address', models.EmailField(error_messages={'unique': 'A user with that Email already exists.'}, max_length=150, unique=True, verbose_name='Email')),
            ],
            options={
                'verbose_name': 'AppUser',
                'verbose_name_plural': 'Users',
                'db_table': 'core_appuser',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_address', models.EmailField(max_length=255)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('recipient_id', models.IntegerField()),
                ('email_campaign_id', models.IntegerField()),
                ('opened', models.BooleanField(default=False)),
                ('clicked', models.BooleanField(default=False)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.appuser')),
            ],
        ),
        migrations.AddConstraint(
            model_name='recipient',
            constraint=models.UniqueConstraint(fields=('recipient_id', 'email_campaign_id', 'from_user'), name='unique_recipient_per_campaign'),
        ),
    ]
