from django.contrib import admin
from . import views
from django.urls import path, include
from .views import (
    LiveInventoryView,
    DeleteVehicleAPIView,
    CombinedVehicleAPIView,
    VehicleDataAPIView,
    AddMaintenanceAPIView,
    MaintenanceRecordDetailView,
    MaintenanceRecordListCreateView,
    MaintenanceRecordExportView,
    VehicleInventoryExportView,
    CreatePaymentAPIView,
    ViewPaymentsAPIView,
    VehicleUpdateAPIView,
    OutboundVehicleAPIView,
    VehiclePaymentSummaryAPIView,
    UpdatePaymentAPIView,
    VehicleCostAPIView,
    CatalogueAPIView,
    UpdateCatalogueAPIView,
    CatalogueDetailAPIView,
    VehicleDetailAPIView,
    InquiryBrokerListCreateAPIView,
    GetOutboundVehiclesAPIView,
    VehicleInquiryListCreateAPIView,
    UpdateOutboundVehicleAPIView,
    SalesStatsAPIView,
    VehicleListView,
    VehicleImageAPIView
)



urlpatterns = [

    # Vehicle Management
    path('inventory/', VehicleListView.as_view(), name='vehicle_inventory'),  # List Vehicles
    path('live-inventory/', LiveInventoryView.as_view(), name='live_inventory'),  # Live Inventory API
    path('delete-vehicle/<int:vehicle_id>/', DeleteVehicleAPIView.as_view(), name='delete_vehicle'),  # Delete Vehicle
    path('vehicle/', CombinedVehicleAPIView.as_view(), name='combined_vehicle'),  # Combined Vehicle API
    path('vehicle/update/<int:vehicle_id>/', VehicleUpdateAPIView.as_view(), name='update-vehicle'),
    path('vehicle-detail/<int:vehicle_id>/', VehicleDetailAPIView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:vehicle_id>/images/', VehicleImageAPIView.as_view(), name='vehicle-images'),

    # payments slot
    path('payments/', CreatePaymentAPIView.as_view(), name='create_payment'),

    # ✅ Retrieve Payments for a Vehicle (GET)
    path('payments/<int:vehicle_id>/', ViewPaymentsAPIView.as_view(), name='retrieve_payments_by_vehicle'),

    # ✅ Update or Add a New Payment Slot for a Vehicle (PUT)
    path('payments/<int:vehicle_id>/<str:slot_number>/', UpdatePaymentAPIView.as_view(), name='update_payment_slot'),

    # Permission Management
    path('all-inventory/', VehicleDataAPIView.as_view(), name='vehicle-data'),
    path('inventory-export/', VehicleInventoryExportView.as_view(), name='vehicle-data'),
    # path('assign-per/', AssignPermissionAPIView.as_view(), name='assign-per'),

    #add maintenance
    path('add-maintenance/', AddMaintenanceAPIView.as_view(), name='add-maintenance'),

    path('maintenance/', MaintenanceRecordListCreateView.as_view(), name='maintenance-list-create'),
    path('maintenance/<int:pk>/', MaintenanceRecordDetailView.as_view(), name='maintenance-detail'),
    path('maintenance/export-excel/', MaintenanceRecordExportView.as_view(), name='maintenance-export-excel'),
    path('outbound-vehicle/', OutboundVehicleAPIView.as_view(), name='create_outbound_vehicle'),  # Create Outbound Vehicle
    path('outbound-vehicle/<int:vehicle_id>/', OutboundVehicleAPIView.as_view(), name='get_outbound_vehicle'),  # Get Outbound Vehicle by vehicle_id
    path('outbound-vehicles/', GetOutboundVehiclesAPIView.as_view(), name='get_outbound_vehicles'),
    path('vehicle-payment-summary/<int:vehicle_id>/', VehiclePaymentSummaryAPIView.as_view(), name='vehicle-payment-summary'),
    path('vehicle-cost/<int:vehicle_id>/', VehicleCostAPIView.as_view(), name='update-payment'),
    path('catalogue/', CatalogueAPIView.as_view(), name='catalogue-list'),
    path('catalogue/<int:vehicle_id>/', CatalogueDetailAPIView.as_view(), name='catalogue-detail'),
    path('catalogue/update/<int:vehicle_id>/', UpdateCatalogueAPIView.as_view(), name='catalogue-update'),

    # path('sales-statistics/', VehicleStatisticsAPIView.as_view(), name='sales-statistics'),

    # # Invoice Management
    # path('invoices/', InvoiceAPIView.as_view(), name='invoice-list-create'),
    # path('invoices/<int:invoice_id>/', InvoiceAPIView.as_view(), name='invoice-detail'),
    # path('invoices/generate-pdf/<int:invoice_id>/', GenerateInvoicePDFView.as_view(), name='generate-invoice-pdf'),

    path('inquiry-brokers/', InquiryBrokerListCreateAPIView.as_view(), name='inquiry-brokers'),
    path('vehicle-inquiries/', VehicleInquiryListCreateAPIView.as_view(), name='vehicle-inquiries'),
    path('outbound/update/<int:vehicle_id>/', UpdateOutboundVehicleAPIView.as_view(), name='update_outbound_vehicle'),
    path('sales-stats/', SalesStatsAPIView.as_view(), name='sales-stats'),

]



