from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['balance', 'created_at', 'updated_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet', 'amount', 'transaction_type', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['wallet__user__username', 'description']
    list_editable = ['status']
    readonly_fields = ['amount', 'transaction_type', 'created_at']