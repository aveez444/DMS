# Generated by Django 4.2.11 on 2025-05-31 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dealership', '0002_alter_vehicle_chassis_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='upload_image_of_vehicle',
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='chassis_number',
            field=models.CharField(max_length=5, verbose_name='Vehicle Identification Number (VIN)'),
        ),
        migrations.CreateModel(
            name='VehicleImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='vehicle_images/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='dealership.vehicle')),
            ],
        ),
    ]
