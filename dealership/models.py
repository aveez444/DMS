from django.db import models
from accounts.models import CustomUser  # Import your user model
from django.conf import settings
from django.utils import timezone

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('bus', 'Bus'),
        ('truck', 'Truck'),
        ('three_wheelers', 'Three Wheelers'),
    ]

    INVENTORY_STATUS_CHOICES = [
        ('IN', 'In Inventory'),
        ('OUT', 'Out of Inventory'),
    ]
    inventory_status = models.CharField(
        max_length=3,
        choices=INVENTORY_STATUS_CHOICES,
        default='IN',
        null=True,
        blank=True
    )
    
    # Vehicle Information
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='car')
    vehicle_id = models.AutoField(primary_key=True)
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    year_of_manufacturing = models.IntegerField()
    year_of_registration = models.IntegerField(null=True, blank=True)
    chassis_number = models.CharField(max_length=5, verbose_name="Vehicle Identification Number (VIN)")
    engine_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    osn_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    license_plate_number = models.CharField(max_length=15, unique=True)
    odometer_reading_kms = models.PositiveIntegerField()
    color = models.CharField(max_length=30)
    fuel_type = models.CharField(max_length=30)
    transmission_type = models.CharField(max_length=30)

    # Seller Information
    seller_name_company_name = models.CharField(max_length=100, null=False, blank=False)
    mobile_number = models.CharField(max_length=15, null=False, blank=False)
    email_address = models.EmailField(null=True, blank=True)
    proof_of_ownership_document = models.FileField(upload_to='ownership_documents/', blank=True, null=True)

    # Condition and Inspection
    inspection_date = models.DateField(null=True, blank=True)
    condition_grade = models.CharField(
        max_length=20,
        choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Poor', 'Poor')],
        null=True, blank=True
    )
    TIRES_CONDITION_CHOICES = [
        ('0-25', '0-25%'), ('25-50', '25-50%'), ('50-75', '50-75%'), ('75-100', '75-100%'),
    ]
    tires_condition = models.CharField(
        max_length=10, choices=TIRES_CONDITION_CHOICES, default='50-75', null=True, blank=True
    )
    damage_details_if_any = models.CharField(max_length=100, null=True, blank=True)
    engine_condition = models.CharField(max_length=100, null=True, blank=True)
    interior_condition = models.CharField(
        max_length=20,
        choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Poor', 'Poor')],
        default='Good', null=True, blank=True
    )
    proof_of_ownership = models.FileField(upload_to='ownership_documents/', blank=True, null=True)

    # Purchase Information
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_of_purchase = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=30, null=True, blank=True)
    purchase_agreement = models.FileField(upload_to='purchase_agreements/', blank=True, null=True)
    arrival_date = models.DateField(null=True, blank=True)
    storage_location = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    estimated_selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    added_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"{self.vehicle_make} - {self.vehicle_model} ({self.license_plate_number})"

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='vehicle_images/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.vehicle.vehicle_make} - {self.vehicle.vehicle_model}"
        
class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('purchase', 'Purchase Payment'),
        ('selling', 'Selling Payment'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
    ]

    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_TYPE_CHOICES,
        default='purchase',
        null=True
    )

    SLOT_CHOICES = [
        ('Slot 1', 'Slot 1'), ('Slot 2', 'Slot 2'), ('Slot 3', 'Slot 3'),
        ('Slot 4', 'Slot 4'), ('Slot 5', 'Slot 5'), ('Slot 6', 'Slot 6'),
        ('Slot 7', 'Slot 7'), ('Slot 8', 'Slot 8'), ('Slot 9', 'Slot 9'), ('Slot 10', 'Slot 10')
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="payments")  
    slot_number = models.CharField(max_length=10, choices=SLOT_CHOICES)  
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)  
    date_of_payment = models.DateField()  
    payment_mode = models.CharField(
        max_length=20, choices=PAYMENT_MODE_CHOICES, null=True, blank=True
    )  # ✅ New Column for Payment Mode
    payment_remark = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.vehicle.license_plate_number} - {self.slot_number} - {self.payment_type} - ₹{self.amount_paid} - {self.payment_mode}"

class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPES = [
        ('oil_change', 'Oil Change'),
        ('tire_replacement', 'Tire Replacement'),
        ('battery_replacement', 'Battery Replacement'),
        ('brake_repair', 'Brake Repair'),
        ('engine_tuning', 'Engine Tuning'),
        ('general_service', 'General Service'),
        ('coolant_refill', 'Coolant Refill'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        db_column='vehicle_id'  # Explicitly map to 'vehicle_id' column
    )
    maintenance_type = models.CharField(max_length=100)
    maintenance_date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    person_in_charge = models.CharField(max_length=100, null=True, blank=True)
    receipt = models.FileField(upload_to='maintenance_receipts/', blank=True, null=True)
    payment_mode = models.CharField(max_length=50, null=True, blank=True)  # ✅ New Field for Payment Mode
    created_at = models.DateTimeField(default=timezone.now)  # Allows manual modification if needed
   
    def __str__(self):
        return f"Maintenance for {self.vehicle.vehicle_make} - {self.maintenance_type}"


class OutboundVehicle(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE)  # Connects to the existing vehicle
    vehicle_current_images = models.ImageField(upload_to="outbound_vehicle_images/", blank=True, null=True)
    vehicle_current_condition = models.CharField(
        max_length=20,
        choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Bad', 'Bad'), ('Worse', 'Worse')],
        default='Good'
    )
    notes = models.TextField(blank=True, null=True)
    buyers_name = models.CharField(max_length=100)
    buyers_contact_details = models.CharField(max_length=15)
    buyers_address = models.TextField(blank=True, null=True)
    buyers_proof_of_identity = models.FileField(upload_to="buyer_proofs/", blank=True, null=True)
    delivery_status = models.CharField(max_length=50, default="Pending")
    outbound_date = models.DateField()
    estimated_delivery_date = models.DateField(blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    other_expense = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Override save() to automatically set the vehicle's inventory_status
        to 'OUT' once an OutboundVehicle record is created or updated.
        """
        super().save(*args, **kwargs)
        self.vehicle.inventory_status = 'OUT'
        self.vehicle.save()

    def __str__(self):
        return f"Outbound Vehicle ID: {self.vehicle.vehicle_id} - {self.buyers_name}"

class Inquirybroker(models.Model):
    company=models.CharField(null=True,max_length=255)
    name=models.CharField(null=False,max_length=255)
    contact=models.CharField(null=False,max_length=255)

class VehicleInquiry(models.Model):
    name=models.CharField(null=True,max_length=255)
    contact=models.CharField(null=True,max_length=255)
    Vehicle_name=models.CharField(null=True,max_length=255)
    budget=models.CharField(null=True,max_length=255)
    model=models.CharField(null=True,max_length=255)

    def __str__(self):
        return f"{self.name} -{self.Vehicle_name}"

# bill record 
class ElectricityBill(models.Model):
    """Model to store electricity bill details"""
    electricity_bill= models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    electricity_bill_date = models.DateField(null=True, blank=True)


class OfficeRent(models.Model):
    """Model to store office rent details"""
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rent_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WifiBill(models.Model):
    """Model to store WiFi bill details"""
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bill_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Staff(models.Model):
    """Model to store staff details"""
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField()

    def __str__(self):
        return self.name

class StaffSalary(models.Model):
    """Model to store staff salary payments"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="salaries")
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()  # Payment Date

    def _str_(self):
        return f"{self.staff.name} - {self.date.strftime('%B %Y')}"    
    
class AdditionalExpense(models.Model):
    expense_type = models.TextField(blank=True, null=True)  # Changed from expense_details
    value = models.TextField(blank=True, null=True)  # Changed from price_details
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expense_type} - {self.value}"


# inVOICE 
class Invoice(models.Model):
    """Model to store invoice details"""
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
    ]

    date = models.DateField()
    invoice_name = models.CharField(max_length=255)
    invoice_no = models.CharField(max_length=50, unique=True)

    # GST, PAN, HSN codes (Sender)
    in_gst = models.CharField(max_length=15)
    in_pan = models.CharField(max_length=10)
    in_hsn_code = models.CharField(max_length=15)

    # GST, PAN, HSN codes (Receiver)
    to_gst = models.CharField(max_length=15)
    to_pan = models.CharField(max_length=10)
    to_hsn_code = models.CharField(max_length=15)

    address = models.TextField()
    description = models.TextField()
    # Amounts & Taxes
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    state_code = models.CharField(max_length=5)
    sgst = models.DecimalField(null=True,blank=True,max_digits=10, decimal_places=2, default=0.00)
    cgst = models.DecimalField(null=True,blank=True,max_digits=10, decimal_places=2, default=0.00)
    igst = models.DecimalField(null=True,blank=True,max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_no} - {self.invoice_name}"
    