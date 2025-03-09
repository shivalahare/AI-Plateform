from django.core.management.base import BaseCommand
from django.utils.text import slugify
from tools.models import Category, Tool
from decimal import Decimal

class Command(BaseCommand):
    help = 'Creates sample categories and tools for testing'

    def handle(self, *args, **kwargs):
        # Create Categories
        categories_data = [
            {
                'name': 'Text Generation',
                'icon': 'fa-solid fa-pen-fancy',
                'description': 'AI tools for generating and manipulating text content'
            },
            {
                'name': 'Image Processing',
                'icon': 'fa-solid fa-image',
                'description': 'Tools for image generation, editing, and enhancement'
            },
            {
                'name': 'Code Assistant',
                'icon': 'fa-solid fa-code',
                'description': 'AI-powered coding and development tools'
            },
            {
                'name': 'Data Analysis',
                'icon': 'fa-solid fa-chart-line',
                'description': 'Tools for analyzing and visualizing data'
            }
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'icon': cat_data['icon'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create Tools
        tools_data = [
            {
                'category': 'Text Generation',
                'name': 'Story Writer Pro',
                'description': 'Generate creative stories and narratives using AI',
                'model_name': 'gpt-4',
                'input_format': {
                    "type": "object",
                    "properties": {
                        "genre": {"type": "string"},
                        "length": {"type": "string"},
                        "theme": {"type": "string"}
                    }
                },
                'output_format': {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "story": {"type": "string"}
                    }
                },
                'cost_per_token': '0.000015'
            },
            {
                'category': 'Image Processing',
                'name': 'AI Image Generator',
                'description': 'Create stunning images from text descriptions',
                'model_name': 'dall-e-3',
                'input_format': {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "style": {"type": "string"},
                        "size": {"type": "string"}
                    }
                },
                'output_format': {
                    "type": "object",
                    "properties": {
                        "image_url": {"type": "string"}
                    }
                },
                'cost_per_token': '0.000080'
            },
            {
                'category': 'Code Assistant',
                'name': 'Code Reviewer',
                'description': 'AI-powered code review and suggestions',
                'model_name': 'gpt-4',
                'input_format': {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"}
                    }
                },
                'output_format': {
                    "type": "object",
                    "properties": {
                        "suggestions": {"type": "array"},
                        "improvements": {"type": "object"}
                    }
                },
                'cost_per_token': '0.000030'
            },
            {
                'category': 'Data Analysis',
                'name': 'Data Insights',
                'description': 'Extract insights from your data using AI',
                'model_name': 'gpt-4',
                'input_format': {
                    "type": "object",
                    "properties": {
                        "data": {"type": "array"},
                        "analysis_type": {"type": "string"}
                    }
                },
                'output_format': {
                    "type": "object",
                    "properties": {
                        "insights": {"type": "array"},
                        "visualizations": {"type": "array"}
                    }
                },
                'cost_per_token': '0.000025'
            }
        ]

        for tool_data in tools_data:
            category = Category.objects.get(name=tool_data['category'])
            tool, created = Tool.objects.get_or_create(
                name=tool_data['name'],
                defaults={
                    'slug': slugify(tool_data['name']),
                    'description': tool_data['description'],
                    'category': category,
                    'model_name': tool_data['model_name'],
                    'input_format': tool_data['input_format'],
                    'output_format': tool_data['output_format'],
                    'cost_per_token': Decimal(tool_data['cost_per_token']),
                    'status': 'active'
                }
            )
            if created:
                self.stdout.write(f'Created tool: {tool.name}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample categories and tools'))
