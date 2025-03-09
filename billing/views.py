from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Plan, Subscription, Invoice
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def pricing(request):
    """Display available pricing plans"""
    plans = Plan.objects.filter(is_active=True).order_by('price')
    current_subscription = None
    
    if request.user.is_authenticated:
        current_subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
    
    return render(request, 'billing/pricing.html', {
        'plans': plans,
        'current_subscription': current_subscription
    })

@login_required
def subscription(request):
    """Display user's subscription details and management options"""
    subscription = Subscription.objects.filter(
        user=request.user,
        status='active'
    ).first()
    
    invoices = Invoice.objects.filter(
        user=request.user
    ).order_by('-created_at')[:12]  # Last 12 invoices
    
    return render(request, 'billing/subscription.html', {
        'subscription': subscription,
        'invoices': invoices
    })

@login_required
def change_plan(request, plan_slug):
    """Handle plan changes"""
    plan = get_object_or_404(Plan, slug=plan_slug, is_active=True)
    
    current_subscription = Subscription.objects.filter(
        user=request.user,
        status='active'
    ).first()
    
    if current_subscription:
        if current_subscription.plan == plan:
            messages.info(request, "You are already subscribed to this plan.")
        else:
            current_subscription.plan = plan
            current_subscription.save()
            messages.success(request, f"Successfully switched to {plan.name} plan!")
    else:
        # Set start_date to now and end_date to 1 month from now
        start_date = timezone.now()
        end_date = start_date + relativedelta(months=1)
        
        Subscription.objects.create(
            user=request.user,
            plan=plan,
            status='active',
            start_date=start_date,
            end_date=end_date
        )
        messages.success(request, f"Successfully subscribed to {plan.name} plan!")
    
    return redirect('billing:subscription')

@login_required
def cancel_subscription(request):
    """Handle subscription cancellation"""
    if request.method == 'POST':
        subscription = get_object_or_404(
            Subscription,
            user=request.user,
            status='active'
        )
        
        subscription.cancel_at_period_end = True
        subscription.save()
        
        messages.success(request, "Your subscription has been scheduled for cancellation at the end of the billing period.")
    
    return redirect('billing:subscription')

@login_required
def reactivate_subscription(request):
    """Handle subscription reactivation"""
    if request.method == 'POST':
        subscription = get_object_or_404(
            Subscription,
            user=request.user,
            status='active'
        )
        
        subscription.cancel_at_period_end = False
        subscription.save()
        
        messages.success(request, "Your subscription has been reactivated.")
    
    return redirect('billing:subscription')

@login_required
def invoice_pdf(request, invoice_id):
    """Generate PDF invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Draw things on the PDF
    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(1*inch, 10*inch, "Invoice")
    
    # Invoice details
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, 9*inch, f"Invoice Number: {invoice.id}")
    p.drawString(1*inch, 8.5*inch, f"Date: {invoice.created_at.strftime('%B %d, %Y')}")
    p.drawString(1*inch, 8*inch, f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}")
    p.drawString(1*inch, 7.5*inch, f"Status: {invoice.status.title()}")
    
    # Customer details
    p.drawString(1*inch, 6.5*inch, "Bill To:")
    p.drawString(1*inch, 6*inch, f"{invoice.user.get_full_name() or invoice.user.username}")
    p.drawString(1*inch, 5.5*inch, f"Email: {invoice.user.email}")
    
    # Subscription details
    if invoice.subscription:
        p.drawString(1*inch, 4.5*inch, "Subscription Details:")
        p.drawString(1*inch, 4*inch, f"Plan: {invoice.subscription.plan.name}")
        p.drawString(1*inch, 3.5*inch, f"Period: {invoice.subscription.start_date.strftime('%B %d, %Y')} - {invoice.subscription.end_date.strftime('%B %d, %Y')}")
    
    # Amount
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*inch, 2*inch, f"Total Amount: ${invoice.amount}")
    
    # Close the PDF object cleanly
    p.showPage()
    p.save()
    
    # Get the value of the BytesIO buffer and write it to the response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    
    return response

