from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Tool, Category, ToolUsage
from dashboard.models import UserActivity  # Add this import
import json

@login_required
def tool_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    
    tools = Tool.objects.filter(status='active')
    if selected_category:
        tools = tools.filter(category__slug=selected_category)
    
    paginator = Paginator(tools, 12)  # Show 12 tools per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'selected_category': selected_category,
        'page_obj': page_obj
    }
    return render(request, 'tools/list.html', context)

@login_required
def tool_detail(request, slug):
    tool = get_object_or_404(Tool, slug=slug, status='active')
    recent_usage = ToolUsage.objects.filter(
        user=request.user,
        tool=tool
    ).order_by('-created_at')[:5]
    
    # Convert the JSON fields to strings
    input_format = json.dumps(tool.input_format, indent=2)
    output_format = json.dumps(tool.output_format, indent=2)
    
    context = {
        'tool': tool,
        'recent_usage': recent_usage,
        'input_format': input_format,
        'output_format': output_format
    }
    return render(request, 'tools/detail.html', context)

@login_required
@require_http_methods(["POST"])
def process_tool(request, slug):
    tool = get_object_or_404(Tool, slug=slug, status='active')
    
    try:
        input_data = json.loads(request.body)
        
        # Here you would implement the actual AI processing logic
        result = process_ai_request(tool, input_data)
        
        # Create ToolUsage record
        usage = ToolUsage.objects.create(
            user=request.user,
            tool=tool,
            tokens_used=result.get('tokens_used', 0),
            cost=result.get('cost', 0),
            success=True
        )

        # Create UserActivity record
        UserActivity.objects.create(
            user=request.user,
            activity_type='tool_usage',
            description=f'Used {tool.name} tool - {usage.tokens_used} tokens'
        )

        return JsonResponse(result)
        
    except Exception as e:
        # Log error activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='error',
            description=f'Error using {tool.name} tool: {str(e)}'
        )
        return JsonResponse({'error': str(e)}, status=400)

def process_ai_request(tool, input_data):
    """
    Placeholder for AI processing logic.
    In a real implementation, this would integrate with your AI services.
    """
    # This is where you'd implement the actual AI processing
    # For now, we'll return dummy data
    return {
        'output': {'result': 'Processed result would go here'},
        'tokens_used': 100,
        'cost': tool.cost_per_token * 100
    }
