from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import UserActivity
from tools.models import ToolUsage  # Change to use ToolUsage instead of Usage

@login_required
def home(request):
    # Get date range for filtering
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get usage statistics using ToolUsage model
    usage_stats = ToolUsage.objects.filter(
        user=request.user,
        created_at__range=[start_date, end_date]
    ).aggregate(
        total_tokens=Sum('tokens_used'),
        total_cost=Sum('cost')
    )

    # Format the statistics with proper defaults and formatting
    formatted_stats = {
        'total_tokens': '{:,}'.format(usage_stats['total_tokens'] or 0),
        'total_cost': '{:.2f}'.format(float(usage_stats['total_cost'] or 0)),
        'daily_average_tokens': '{:,}'.format(
            int((usage_stats['total_tokens'] or 0) / 30)
        ),
        'daily_average_cost': '{:.2f}'.format(
            float(usage_stats['total_cost'] or 0) / 30
        )
    }

    # Get most used tools with percentage calculation using ToolUsage
    most_used_tools = ToolUsage.objects.filter(
        user=request.user,
        created_at__range=[start_date, end_date]
    ).values(
        'tool__name'  # Use tool__name instead of tool_name
    ).annotate(
        total_uses=Count('id'),
        total_tokens=Sum('tokens_used'),
        total_cost=Sum('cost')
    ).order_by('-total_uses')[:5]

    # Calculate total uses for percentage
    total_tool_uses = sum(tool['total_uses'] for tool in most_used_tools)
    
    # Add percentage and format tool data
    formatted_tools = []
    for tool in most_used_tools:
        usage_percentage = (
            (tool['total_uses'] / total_tool_uses * 100)
            if total_tool_uses > 0 else 0
        )
        formatted_tools.append({
            'tool_name': tool['tool__name'],
            'total_uses': tool['total_uses'],
            'total_tokens': '{:,}'.format(tool['total_tokens']),
            'total_cost': '{:.2f}'.format(float(tool['total_cost'])),
            'usage_percentage': usage_percentage
        })

    context = {
        'usage_stats': formatted_stats,
        'most_used_tools': formatted_tools,
        'recent_activity': UserActivity.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10],
        'date_range': {
            'start': start_date.strftime('%B %d'),
            'end': end_date.strftime('%B %d')
        }
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def statistics(request):
    # Get monthly usage data
    monthly_usage = ToolUsage.objects.filter(
        user=request.user,
        created_at__gte=timezone.now() - timedelta(days=365)
    ).values('created_at__month').annotate(
        total_tokens=Sum('tokens_used'),
        total_cost=Sum('cost')
    ).order_by('created_at__month')

    # Get tool-wise usage
    tool_usage = ToolUsage.objects.filter(
        user=request.user
    ).values('tool__name').annotate(
        total_tokens=Sum('tokens_used'),
        total_cost=Sum('cost'),
        usage_count=Count('id')
    ).order_by('-usage_count')

    context = {
        'monthly_usage': list(monthly_usage),  # Convert to list for JSON serialization
        'tool_usage': list(tool_usage),
    }
    return render(request, 'dashboard/statistics.html', context)

@login_required
def settings(request):
    if request.method == 'POST':
        # Handle settings update logic here
        # ...
        
        # Record the activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='settings_update',
            description='Updated account settings'
        )
        
    context = {
        'user': request.user,
    }
    return render(request, 'dashboard/settings.html', context)
