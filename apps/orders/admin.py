from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False


def mark_as_processing(modeladmin, request, queryset):
    queryset.update(status=Order.Status.PROCESSING)
mark_as_processing.short_description = _("Mark selected orders as processing")


def mark_as_shipped(modeladmin, request, queryset):
    queryset.update(status=Order.Status.SHIPPED)
mark_as_shipped.short_description = _("Mark selected orders as shipped")


def mark_as_delivered(modeladmin, request, queryset):
    queryset.update(status=Order.Status.DELIVERED)
mark_as_delivered.short_description = _("Mark selected orders as delivered")


def mark_as_cancelled(modeladmin, request, queryset):
    queryset.update(status=Order.Status.CANCELLED)
mark_as_cancelled.short_description = _("Cancel selected orders")


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    list_display = ('id', 'email', 'status', 'total_cost', 'created_at', 'paid')
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('id', 'email', 'first_name', 'last_name')
    list_editable = ('status', 'paid')
    readonly_fields = ('created_at', 'updated_at', 'total_cost')
    inlines = [OrderItemInline]
    actions = [mark_as_processing, mark_as_shipped, mark_as_delivered, mark_as_cancelled]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'guest_session')
        }),
        (_('Customer information'), {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        (_('Shipping information'), {
            'fields': ('address', 'postal_code', 'city')
        }),
        (_('Order information'), {
            'fields': ('status', 'paid', 'total_cost')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Редактирование существующего объекта
            return self.readonly_fields + ('user', 'guest_session', 'first_name', 'last_name', 'email', 'phone', 
                                         'address', 'postal_code', 'city')
        return self.readonly_fields


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity', 'get_cost')
    list_filter = ('created_at',)
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('order', 'product', 'price', 'quantity', 'created_at', 'updated_at')
    
    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = _('Cost')
