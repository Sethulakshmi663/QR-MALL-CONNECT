from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
import qrcode
import io
import base64
from .models import Product, Review, Category

# Product List + Search + Filter + Pagination
def product_list(request):
    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'name')
    
    products = Product.objects.filter(available=True)
    
    # Enhanced search by name,  or category
    if q:
        products = products.filter(
            Q(name__icontains=q) | 
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        ).distinct()
    
    # Filter by category
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(products, 20)  # Show products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter dropdown
    categories = Category.objects.annotate(product_count=Count('product')).filter(product_count__gt=0)
    
    # Get popular searches (this would be enhanced with a proper analytics model)
    popular_categories = categories.order_by('-product_count')[:5]
    
    context = {
        'products': page_obj,
        'categories': categories,
        'popular_categories': popular_categories,
        'q': q,
        'selected_category': category_id,
        'sort_by': sort_by,
        'total_products': products.count(),
    }
    return render(request, 'products/list.html', context)


# Product Detail + Reviews + Offers
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Handle review form
    if request.method == 'POST':
        name = request.POST.get('name', 'Anonymous')
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        Review.objects.create(product=product, name=name, rating=rating, comment=comment)
        return redirect('product_detail', pk=pk)

    offers = product.offers.all()
    reviews = product.reviews.all()

    # Generate QR code for product
    product_url = request.build_absolute_uri()
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(product_url)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'products/detail.html', {
        'product': product,
        'offers': offers,
        'reviews': reviews,
        'qr_code': qr_code_base64,
    })

def generate_product_qr(request, pk):
    """Generate customizable QR code for a specific product"""
    product = get_object_or_404(Product, pk=pk)
    product_url = request.build_absolute_uri(f'/{pk}/')
    
    # Get customization parameters
    size = int(request.GET.get('size', '10'))
    border = int(request.GET.get('border', '4'))
    fill_color = request.GET.get('fill_color', 'black')
    back_color = request.GET.get('back_color', 'white')
    
    # Create QR code with custom settings
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=border
    )
    qr.add_data(product_url)
    qr.make(fit=True)
    
    # Create image with custom colors
    try:
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
    except:
        # Fallback to default colors if custom colors are invalid
        img = qr.make_image(fill_color="black", back_color="white")
    
    # Return as HTTP response
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    
    # Clean filename
    clean_name = ''.join(c for c in product.name if c.isalnum() or c in (' ', '-', '_')).strip()
    response['Content-Disposition'] = f'attachment; filename="QR_{clean_name}.png"'
    return response

# Search Suggestions API
@cache_page(60 * 5)  # Cache for 5 minutes
def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []
    
    if len(query) >= 2:  # Only suggest after 2+ characters
        # Get product name suggestions
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).values('name')[:5]
        
        # Get category suggestions
        categories = Category.objects.filter(
            name__icontains=query
        ).values('name')[:3]
        
        # Combine suggestions
        suggestions.extend([p['name'] for p in products])
        suggestions.extend([f"Category: {c['name']}" for c in categories])
    
    return JsonResponse({'suggestions': suggestions[:8]})

# Batch QR Code Generation
def batch_qr_generation(request):
    """Generate QR codes for multiple products"""
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        
        if not product_ids:
            return JsonResponse({'error': 'No products selected'}, status=400)
        
        products = Product.objects.filter(id__in=product_ids)
        qr_data = []
        
        for product in products:
            product_url = request.build_absolute_uri(f'/{product.id}/')
            
            # Create QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(product_url)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            qr_data.append({
                'id': product.id,
                'name': product.name,
                'qr_code': qr_code_base64
            })
        
        return JsonResponse({'qr_codes': qr_data})
    
    # GET request - show batch generation form
    products = Product.objects.filter(available=True).order_by('name')
    return render(request, 'products/batch_qr.html', {'products': products})

