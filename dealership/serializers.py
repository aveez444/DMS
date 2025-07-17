from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Vehicle, VehicleImage, MaintenanceRecord, OutboundVehicle, Payment, Inquirybroker, VehicleInquiry, Staff,StaffSalary,Invoice,ElectricityBill, OfficeRent, WifiBill, AdditionalExpense
from rest_framework.serializers import Serializer
User = get_user_model()
from django.db.models import Sum


class VehicleImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'image_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

        
class CombinedVehicleSerializer(serializers.ModelSerializer):
    proof_of_ownership_url = serializers.SerializerMethodField()
    purchase_agreement_url = serializers.SerializerMethodField()
    vehicle_images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            # Vehicle Information
            'vehicle_id', 'vehicle_type', 'vehicle_make', 'vehicle_model', 'year_of_manufacturing',
            'year_of_registration', 'chassis_number', 'engine_number', 'osn_number',
            'license_plate_number', 'odometer_reading_kms', 'color', 'fuel_type', 'transmission_type',

            # Seller Information
            'seller_name_company_name', 'mobile_number', 'email_address', 'proof_of_ownership_document',
            'proof_of_ownership_url',

            # Condition and Inspection
            'inspection_date', 'condition_grade', 'tires_condition', 'damage_details_if_any',
            'engine_condition', 'interior_condition', 'vehicle_images',

            # Purchase Information
            'purchase_price', 'date_of_purchase', 'payment_method', 'purchase_agreement',
            'purchase_agreement_url', 'arrival_date', 'storage_location', 'notes',
        ]
        read_only_fields = ['vehicle_id']

    def get_proof_of_ownership_url(self, obj):
        request = self.context.get('request')
        if obj.proof_of_ownership_document and request:
            return request.build_absolute_uri(obj.proof_of_ownership_document.url)
        return None

    def get_purchase_agreement_url(self, obj):
        request = self.context.get('request')
        if obj.purchase_agreement and request:
            return request.build_absolute_uri(obj.purchase_agreement.url)
        return None

    def create(self, validated_data):
        images_data = self.context['request'].FILES.getlist('vehicle_images', [])
        validated_data.pop('vehicle_images', None)  # Remove vehicle_images if present
        vehicle = Vehicle.objects.create(**validated_data, added_by=self.context['request'].user)
        for image_data in images_data:
            VehicleImage.objects.create(vehicle=vehicle, image=image_data)
        return vehicle


class OutboundVehicleSerializer(serializers.ModelSerializer):
    # Vehicle details
    vehicle_make = serializers.CharField(source='Vehicle.vehicle_make', read_only=True)
    vehicle_model = serializers.CharField(source='Vehicle.vehicle_model', read_only=True)
    license_plate_number = serializers.CharField(source='Vehicle.license_plate_number', read_only=True)
    
    class Meta:
        model = OutboundVehicle
        fields = [
            'id',
            'vehicle',  # Keep the vehicle ID reference
            'vehicle_make',
            'vehicle_model',
            'license_plate_number',
            'vehicle_current_images',
            'vehicle_current_condition',
            'notes',
            'buyers_name',
            'buyers_contact_details',
            'buyers_address',
            'buyers_proof_of_identity',
            'delivery_status',
            'outbound_date',
            'estimated_delivery_date',
            'selling_price',
            'other_expense',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class PaymentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating or adding a payment for a specific slot.
    """
    class Meta:
        model = Payment
        fields = ['vehicle', 'slot_number', 'amount_paid', 'date_of_payment', 'payment_remark']

    def validate(self, data):
        """
        Ensure valid data and slot selection.
        """
        slot_number = data.get('slot_number')
        if slot_number not in dict(Payment.SLOT_CHOICES):
            raise serializers.ValidationError({"slot_number": "Invalid slot selected."})
        return data

class VehicleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Vehicle model instances. 
    This handles the unique constraints for engine_number and osn_number.
    """
    class Meta:
        model = Vehicle
        exclude = ['added_by']  # Exclude fields that shouldn't be updated via API
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional for partial updates
        for field in self.fields:
            self.fields[field].required = False

    def to_internal_value(self, data):
        """
        Pre-process the data before validation.
        Convert 'null' strings and empty strings to None for specific fields.
        """
        mutable_data = data.copy() if hasattr(data, 'copy') else data
        
        # Fields that should be None when empty
        nullable_fields = ['engine_number', 'osn_number', 'email_address', 
                         'year_of_registration', 'damage_details_if_any', 
                         'engine_condition', 'interior_condition', 'notes']
        
        # Convert empty strings and "null" strings to None
        for field in nullable_fields:
            if field in mutable_data and (mutable_data[field] == '' or mutable_data[field] == 'null'):
                mutable_data[field] = None
        
        return super().to_internal_value(mutable_data)
    
    def validate_engine_number(self, value):
        """
        Validate engine_number to handle the unique constraint properly.
        """
        # If value is None (already converted in to_internal_value), just return it
        if value is None:
            return None
        
        # Check if this engine number exists on another vehicle
        instance = self.instance
        if Vehicle.objects.exclude(pk=instance.pk).filter(engine_number=value).exists():
            raise serializers.ValidationError("Vehicle with this engine number already exists.")
        return value
    
    def validate_osn_number(self, value):
        """
        Validate osn_number to handle the unique constraint properly.
        """
        # If value is None (already converted in to_internal_value), just return it
        if value is None:
            return None
        
        # Check if this OSN number exists on another vehicle
        instance = self.instance
        if Vehicle.objects.exclude(pk=instance.pk).filter(osn_number=value).exists():
            raise serializers.ValidationError("Vehicle with this OSN number already exists.")
        return value
    
    def validate_license_plate_number(self, value):
        """
        Validate license_plate_number to handle the unique constraint properly.
        """
        # Since license_plate_number is required, we shouldn't set it to None
        if not value:  # Checking if empty or None
            raise serializers.ValidationError("License plate number cannot be empty.")
            
        instance = self.instance
        if Vehicle.objects.exclude(pk=instance.pk).filter(license_plate_number=value).exists():
            raise serializers.ValidationError("Vehicle with this license plate number already exists.")
        return value

class VehicleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['vehicle_make', 'vehicle_model', 'license_plate_number', 'odometer_reading_kms', 'condition_grade']

class MaintenanceRecordSerializer(serializers.ModelSerializer):
    # Accept vehicle_id directly from the payload
    vehicle_id = serializers.IntegerField(write_only=True)  # Input only
    vehicle = serializers.CharField(source='vehicle.vehicle_id', read_only=True)  # Output only (vehicle_id)
    vehicle_make = serializers.CharField(source="vehicle.vehicle_make", read_only=True)
    license_plate_number = serializers.CharField(source="vehicle.license_plate_number", read_only=True)
    receipt_url = serializers.SerializerMethodField()  # Add this for absolute URL

    class Meta:
        model = MaintenanceRecord
        fields = [
            'id',
            'vehicle_id',  # Input field
            'vehicle',  # Output field (linked vehicle_id)
            'vehicle_make',  # Displays vehicle name
            'license_plate_number',  # Displays vehicle number plate
            'maintenance_type',
            'maintenance_date',
            'cost',
            'person_in_charge',
            'receipt',  # Keep for backward compatibility or remove if only using receipt_url
            'receipt_url',  # New field for absolute URL
            'created_at',
        ]

    def get_receipt_url(self, obj):
            request = self.context.get('request')
            if obj.receipt and request:
                return request.build_absolute_uri(obj.receipt.url)
            return None

    def create(self, validated_data):
        # Extract 'vehicle_id' from validated_data
        vehicle_id = validated_data.pop('vehicle_id')

        # Validate if vehicle exists
        try:
            vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError({"vehicle_id": "Vehicle not found."})

        # Assign the vehicle object to the record
        validated_data['vehicle'] = vehicle

        # Create and return the maintenance record
        return MaintenanceRecord.objects.create(**validated_data)


class VehicleDataSerializer(serializers.ModelSerializer):
    proof_of_ownership_url = serializers.SerializerMethodField()
    purchase_agreement_url = serializers.SerializerMethodField()
    vehicle_images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            # Vehicle Information
            'vehicle_id', 'vehicle_type', 'vehicle_make', 'vehicle_model', 'year_of_manufacturing',
            'chassis_number', 'license_plate_number', 'odometer_reading_kms', 'color',
            'fuel_type', 'transmission_type', 'inventory_status',

            # Seller Information
            'seller_name_company_name', 'mobile_number', 'email_address', 'proof_of_ownership_document',
            'proof_of_ownership_url', 'inspection_date', 'condition_grade', 'tires_condition',
            'damage_details_if_any', 'engine_condition', 'interior_condition', 'vehicle_images',

            # Purchase Information
            'purchase_price', 'date_of_purchase', 'payment_method', 'purchase_agreement',
            'purchase_agreement_url', 'arrival_date', 'storage_location', 'notes',
        ]

    def get_proof_of_ownership_url(self, obj):
        request = self.context.get('request')
        if obj.proof_of_ownership_document and request:
            return request.build_absolute_uri(obj.proof_of_ownership_document.url)
        return None

    def get_purchase_agreement_url(self, obj):
        request = self.context.get('request')
        if obj.purchase_agreement and request:
            return request.build_absolute_uri(obj.purchase_agreement.url)
        return None


class OutboundVehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving outbound vehicle records.
    """

    class Meta:
        model = OutboundVehicle
        fields = [
            "vehicle", "vehicle_current_images", "vehicle_current_condition",
            "notes", "buyers_name", "buyers_contact_details", "buyers_address",
            "buyers_proof_of_identity", "delivery_status", "outbound_date",
            "estimated_delivery_date", "selling_price", "other_expense", "created_at"
        ]
        read_only_fields = ["created_at"]  # Ensures created_at is not modifiable by users

        
class PaymentSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.IntegerField()

    class Meta:
        model = Payment
        fields = ['vehicle_id', 'slot_number', 'amount_paid',"payment_mode", 'date_of_payment', 'payment_remark','payment_type']

class CatalogueSerializer(serializers.ModelSerializer):
    """
    Serializer for vehicle catalogue. Displays only necessary details.
    """
    selling_price = serializers.SerializerMethodField()
    vehicle_image_urls = serializers.SerializerMethodField()  # Changed to plural since we'll return multiple URLs

    class Meta:
        model = Vehicle
        fields = [
            "vehicle_id", "vehicle_make", "vehicle_model", "year_of_manufacturing",
            "odometer_reading_kms", "fuel_type", "transmission_type",
            "condition_grade", 'vehicle_image_urls', "selling_price"
        ]

    def get_selling_price(self, obj):
        """
        Return estimated_selling_price but display it as 'Selling Price'.
        """
        return obj.estimated_selling_price if obj.estimated_selling_price else "Price on Request"

    def get_vehicle_image_urls(self, obj):
        """
        Return URLs for all vehicle images from VehicleImage model.
        """
        request = self.context.get('request')
        if obj.images.exists() and request:
            return [request.build_absolute_uri(image.image.url) for image in obj.images.all()]
        return None
class UpdateCatalogueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "vehicle_id",
            "vehicle_make",
            "vehicle_model",
            "odometer_reading_kms",
            "condition_grade",
            "estimated_selling_price",
        ]
        read_only_fields = ["vehicle_id", "vehicle_make", "vehicle_model"]

    def validate_estimated_selling_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Estimated selling price cannot be negative.")
        return value

    def update(self, instance, validated_data):
        """
        Handle updating vehicle details.
        """
        instance = super().update(instance, validated_data)
        return instance

class VehicleDetailSerializer(serializers.ModelSerializer):
    proof_of_ownership_url = serializers.SerializerMethodField()
    purchase_agreement_url = serializers.SerializerMethodField()
    vehicle_images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            # Vehicle Info
            'vehicle_id', 'vehicle_type', 'vehicle_make', 'vehicle_model', 'year_of_manufacturing',
            'chassis_number', 'license_plate_number', 'odometer_reading_kms', 'color',
            'fuel_type', 'transmission_type', 'inventory_status', 'year_of_registration',
            'engine_number', 'osn_number',

            # Seller Info
            'seller_name_company_name', 'mobile_number', 'email_address', 'proof_of_ownership',
            'proof_of_ownership_url', 'inspection_date', 'condition_grade', 'tires_condition',
            'damage_details_if_any', 'engine_condition', 'interior_condition', 'vehicle_images',

            # Purchase Info
            'purchase_price', 'date_of_purchase', 'payment_method', 'purchase_agreement',
            'purchase_agreement_url', 'arrival_date', 'storage_location', 'notes',
        ]

    def get_proof_of_ownership_url(self, obj):
        request = self.context.get('request')
        if obj.proof_of_ownership and request:
            return request.build_absolute_uri(obj.proof_of_ownership.url)
        return None

    def get_purchase_agreement_url(self, obj):
        request = self.context.get('request')
        if obj.purchase_agreement and request:
            return request.build_absolute_uri(obj.purchase_agreement.url)
        return None

class InquiryBrokerSerializer(serializers.ModelSerializer):
    """
    Serializer for InquiryBroker model to create and list brokers.
    """
    class Meta:
        model = Inquirybroker
        fields = ['id', 'company', 'name', 'contact']


class VehicleInquirySerializer(serializers.ModelSerializer):
    """
    Serializer for VehicleInquiry model to create and list vehicle inquiries.
    """
    class Meta:
        model = VehicleInquiry
        fields = ['id', 'name', 'contact', 'Vehicle_name', 'budget', 'model']
        
class ElectricityBillSerializer(serializers.ModelSerializer):
    """Serializer for Electricity Bill"""
    class Meta:
        model = ElectricityBill
        fields = "_all_"

class OfficeRentSerializer(serializers.ModelSerializer):
    """Serializer for Office Rent"""
    class Meta:
        model = OfficeRent
        fields = "_all_"

class WifiBillSerializer(serializers.ModelSerializer):
    """Serializer for WiFi Bill"""
    class Meta:
        model = WifiBill
        fields = "_all_"

class AdditionalExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Additional Expenses"""
    class Meta:
        model = AdditionalExpense
        fields = "_all_"

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '_all_'  # Includes name, contact, address

class StaffSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSalary
        fields = '_all_'  # Includes staff, salary, date

class StaffSalaryMonthWiseSerializer(serializers.ModelSerializer):
    """Serializer to return staff details in month-wise settlement format"""
    staff_name = serializers.CharField(source="staff.name")
    contact = serializers.CharField(source="staff.contact")
    address = serializers.CharField(source="staff.address")

    class Meta:
        model = StaffSalary
        fields = ["staff_name", "contact", "address", "salary", "date"]

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '_all_'