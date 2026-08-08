# MYRON Perfume Views
import json

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.db.models import Max, Min, Q
from django.views.decorators.http import require_POST

from .models import Product
from .cart import Cart

PAGE_SIZE = 9


def home(request):
    featured = Product.objects.filter(is_active=True).order_by("-is_new", "-is_bestseller", "-created_at")[:1]
    hero_product = featured[0] if featured else None
    latest_products = Product.objects.filter(is_active=True).order_by("-created_at")[:6]
    price_bounds = Product.objects.filter(is_active=True).aggregate(
        min_price=Min("price"),
        max_price=Max("price"),
    )
    min_available_price = int(price_bounds["min_price"] or 0)
    max_available_price = int(price_bounds["max_price"] or 0)
    context = {
        "hero_product": hero_product,
        "products": latest_products,
        "gender_choices": [(code, Product.gender_label_for(code)) for code, _ in Product.GENDER_CHOICES],
        "concentration_choices": Product.get_concentration_choices_localized(),
        "min_available_price": min_available_price,
        "max_available_price": max_available_price,
        "current_min_price": min_available_price,
        "current_max_price": max_available_price,
    }
    return render(request, "shop/home.html", context)


def _filtered_queryset(request):
    qs = Product.objects.filter(is_active=True)

    gender = request.GET.get("gender", "all")
    if gender in dict(Product.GENDER_CHOICES):
        qs = qs.filter(gender=gender)

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name_uz__icontains=q) | Q(name_ru__icontains=q) | Q(brand__icontains=q))

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        try:
            qs = qs.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(price__lte=float(max_price))
        except ValueError:
            pass

    concentration = request.GET.get("concentration")
    if concentration in dict(Product.CONCENTRATION_CHOICES):
        qs = qs.filter(concentration=concentration)

    sort = request.GET.get("sort", "popular")
    sort_map = {
        "popular": "-reviews_count",
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-created_at",
        "rating": "-rating",
    }
    qs = qs.order_by(sort_map.get(sort, "-reviews_count"))
    return qs


def product_list(request):
    qs = _filtered_queryset(request)
    price_bounds = Product.objects.filter(is_active=True).aggregate(
        min_price=Min("price"),
        max_price=Max("price"),
    )
    min_available_price = int(price_bounds["min_price"] or 0)
    max_available_price = int(price_bounds["max_price"] or 0)
    current_min_price = request.GET.get("min_price") or min_available_price
    current_max_price = request.GET.get("max_price") or max_available_price

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    from_home = request.GET.get("home") == "1"

    # When filtering from the home page, return ALL products (no pagination)
    if is_ajax and from_home:
        html = render_to_string(
            "shop/_product_cards.html", {"products": qs}, request=request
        )
        return JsonResponse({
            "html": html,
            "has_next": False,
            "next_page": None,
            "count": qs.count(),
        })

    page_number = int(request.GET.get("page", 1))
    paginator = Paginator(qs, PAGE_SIZE)
    page_obj = paginator.get_page(page_number)

    if is_ajax:
        html = render_to_string(
            "shop/_product_cards.html", {"products": page_obj.object_list}, request=request
        )
        return JsonResponse({
            "html": html,
            "has_next": page_obj.has_next(),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            "count": paginator.count,
        })

    context = {
        "page_obj": page_obj,
        "has_next": page_obj.has_next(),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        "count": paginator.count,
        "gender_choices": [(code, Product.gender_label_for(code)) for code, _ in Product.GENDER_CHOICES],
        "concentration_choices": Product.get_concentration_choices_localized(),
        "current_gender": request.GET.get("gender", "all"),
        "current_sort": request.GET.get("sort", "popular"),
        "current_q": request.GET.get("q", ""),
        "min_available_price": min_available_price,
        "max_available_price": max_available_price,
        "current_min_price": current_min_price,
        "current_max_price": current_max_price,
    }
    return render(request, "shop/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = (
        Product.objects.filter(is_active=True, gender=product.gender)
        .exclude(pk=product.pk)[:4]
    )
    return render(request, "shop/product_detail.html", {"product": product, "related": related})


# ---------------------------------------------------------------------------
# Cart AJAX endpoints
# ---------------------------------------------------------------------------

def _cart_response(request, cart):
    html = render_to_string(
        "shop/_cart_drawer.html",
        {"cart_items": cart.get_items(), "cart_total": cart.get_total_price()},
        request=request,
    )
    return JsonResponse({
        "count": len(cart),
        "total": str(cart.get_total_price()),
        "html": html,
    })


def cart_detail(request):
    cart = Cart(request)
    return _cart_response(request, cart)


@require_POST
def cart_add(request):
    try:
        data = json.loads(request.body) if request.body else request.POST
    except json.JSONDecodeError:
        data = request.POST
    product_id = data.get("product_id")
    variant_code = data.get("variant_code") or "full"
    quantity = int(data.get("quantity", 1))
    if not product_id:
        return HttpResponseBadRequest("product_id required")
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = Cart(request)
    cart.add(product, quantity, variant_code)
    return _cart_response(request, cart)


@require_POST
def cart_update(request):
    try:
        data = json.loads(request.body) if request.body else request.POST
    except json.JSONDecodeError:
        data = request.POST
    product_id = data.get("product_id")
    variant_code = data.get("variant_code") or "full"
    quantity = int(data.get("quantity", 1))
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.set_quantity(product, quantity, variant_code)
    return _cart_response(request, cart)


@require_POST
def cart_remove(request):
    try:
        data = json.loads(request.body) if request.body else request.POST
    except json.JSONDecodeError:
        data = request.POST
    product_id = data.get("product_id")
    variant_code = data.get("variant_code") or "full"
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product, variant_code)
    return _cart_response(request, cart)


def delivery_terms(request):
    return render(request, "shop/delivery_terms.html")
