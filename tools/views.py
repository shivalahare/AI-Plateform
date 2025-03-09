from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Tool, Category, ToolUsage, models
from dashboard.models import UserActivity  # Add this import
from billing.models import Subscription
import json
from django.db import transaction
from .decorators import check_subscription_limits
from accounts.models import UserProfile

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
    # Add activity for tool view
    UserActivity.objects.create(
        user=request.user,
        activity_type='tool_view',
        description=f'Viewed tool: {tool.name}'
    )
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
@check_subscription_limits  # This decorator now handles the API call increment
@require_http_methods(["POST"])
def process_tool(request, slug):
    tool = get_object_or_404(Tool, slug=slug, status='active')
    subscription = Subscription.objects.get(user=request.user)
    
    try:
        with transaction.atomic():
            input_data = json.loads(request.body)
            
            # Process tool logic here
            result = process_ai_request(tool, input_data)
            
            # Create usage record
            ToolUsage.objects.create(
                user=request.user,
                tool=tool,
                input_data=input_data,
                output_data=result['output'],
                tokens_used=result['tokens_used'],
                cost=result['cost']
            )
            
            return JsonResponse({
                'success': True,
                'data': result['output'],
                'usage': {
                    'tokens': result['tokens_used'],
                    'cost': result['cost'],
                    'remaining_calls': subscription.plan.api_calls_limit - request.user.userprofile.api_calls_count
                }
            })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Internal server error'}, status=500)

def process_ai_request(tool, input_data):
    """
    Process the AI request and validate input against the tool's schema.
    """
    try:
        # Validate input data structure
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a JSON object")

        # Get schema properties
        schema = tool.input_format
        if not schema.get('type') == 'object' or 'properties' not in schema:
            raise ValueError("Invalid schema format")

        properties = schema['properties']

        # Validate each field against the schema
        for field_name, field_spec in properties.items():
            # Check if field exists in input
            if field_name in input_data:
                # Validate field type
                if field_spec.get('type') == 'string':
                    if not isinstance(input_data[field_name], str):
                        raise ValueError(f"Field '{field_name}' must be a string")
                # Add more type validations as needed (number, boolean, etc.)

        # Check for required fields if specified in schema
        required_fields = schema.get('required', list(properties.keys()))
        missing_fields = [
            field for field in required_fields
            if field not in input_data or not input_data[field]
        ]

        if missing_fields:
            raise ValueError(f"Missing or empty required fields: {', '.join(missing_fields)}")

        # Simulate AI processing
        tokens_used = 100
        cost = float(tool.cost_per_token * tokens_used)

        # Generate output based on the tool type
        if tool.name == "Story Writer Pro":
            output = {
                "title": f"A {input_data.get('genre', 'mysterious')} story",
                "story": (
                    f"Once upon a time in a {input_data.get('setting', 'distant land')}, "
                    f"there was a {input_data.get('character_type', 'brave hero')}. "
                    f"This is a {input_data.get('length', 'short')} {input_data.get('genre', 'story')} "
                    f"about {input_data.get('theme', 'adventure')}..."
                )
            }
        else:
            # Default output for other tools
            output = {
                "result": f"Processed {tool.name} with input: {json.dumps(input_data)}"
            }

        return {
            'output': output,
            'tokens_used': tokens_used,
            'cost': cost
        }

    except Exception as e:
        raise ValueError(f"Error processing request: {str(e)}")
