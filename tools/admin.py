from django.contrib import admin
from .models import Category, Tool, ToolUsage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'cost_per_token', 'created_at')
    list_filter = ('category', 'status')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

@admin.register(ToolUsage)
class ToolUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'tool', 'tokens_used', 'cost', 'success', 'created_at')
    list_filter = ('tool', 'success', 'created_at')
    search_fields = ('user__username', 'tool__name')
    date_hierarchy = 'created_at'
