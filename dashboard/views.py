from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from orders.models import Order
from shop.models import Product, SiteSettings

from .forms import OrderStatusForm, ProductForm, SiteSettingsForm, StaffLoginForm


def _is_staff(user):
    return user.is_active and user.is_staff


def staff_required(view_func):
    return user_passes_test(_is_staff, login_url="dashboard:login")(view_func)


def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard:home")

    form = StaffLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user and user.is_staff:
            login(request, user)
            next_url = request.GET.get("next") or reverse("dashboard:home")
            return redirect(next_url)
        messages.error(request, "Login yoki parol noto'g'ri, yoki foydalanuvchi staff emas.")

    return render(request, "dashboard/login.html", {"form": form})


@staff_required
def dashboard_logout(request):
    logout(request)
    return redirect("dashboard:login")


@staff_required
def dashboard_home(request):
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status=Order.STATUS_DONE).count()
    fulfillment_rate = round((completed_orders / total_orders * 100), 1) if total_orders > 0 else 100.0

    stats = {
        "products": Product.objects.count(),
        "active_products": Product.objects.filter(is_active=True).count(),
        "new_orders": Order.objects.filter(status=Order.STATUS_NEW).count(),
        "processing_orders": Order.objects.filter(status=Order.STATUS_CONFIRMED).count(),
        "orders": total_orders,
        "revenue": Order.objects.filter(status=Order.STATUS_DONE).aggregate(total=Sum("total_price"))["total"] or 0,
        "avg_order": Order.objects.filter(status=Order.STATUS_DONE).aggregate(avg=Avg("total_price"))["avg"] or 0,
        "fulfillment_rate": fulfillment_rate,
    }
    recent_orders = Order.objects.prefetch_related("items")[:6]
    low_stock = Product.objects.filter(stock__lte=5).order_by("stock", "name_uz")[:6]
    status_counts = dict(Order.objects.values("status").annotate(total=Count("id")).values_list("status", "total"))

    return render(
        request,
        "dashboard/home.html",
        {
            "stats": stats,
            "recent_orders": recent_orders,
            "low_stock": low_stock,
            "status_counts": status_counts,
            "status_choices": Order.STATUS_CHOICES,
        },
    )


@staff_required
def analytics_view(request):
    total_orders = Order.objects.count()
    completed_revenue = Order.objects.filter(status=Order.STATUS_DONE).aggregate(total=Sum("total_price"))["total"] or 0
    pending_revenue = Order.objects.filter(status__in=[Order.STATUS_NEW, Order.STATUS_CONFIRMED]).aggregate(total=Sum("total_price"))["total"] or 0
    avg_order_value = Order.objects.exclude(status=Order.STATUS_CANCELLED).aggregate(avg=Avg("total_price"))["avg"] or 0

    gender_stats = Product.objects.values("gender").annotate(total_products=Count("id"), avg_price=Avg("price"))
    status_breakdown = Order.objects.values("status").annotate(total=Count("id"), total_sum=Sum("total_price"))
    top_products = Product.objects.filter(is_active=True).order_by("-stock")[:5]

    return render(
        request,
        "dashboard/analytics.html",
        {
            "total_orders": total_orders,
            "completed_revenue": completed_revenue,
            "pending_revenue": pending_revenue,
            "avg_order_value": avg_order_value,
            "gender_stats": gender_stats,
            "status_breakdown": status_breakdown,
            "top_products": top_products,
        },
    )


@staff_required
def product_list(request):
    products = Product.objects.all()
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    gender = request.GET.get("gender", "")
    stock_filter = request.GET.get("stock", "")

    if q:
        products = products.filter(Q(name_uz__icontains=q) | Q(name_ru__icontains=q) | Q(brand__icontains=q))
    if status == "active":
        products = products.filter(is_active=True)
    elif status == "inactive":
        products = products.filter(is_active=False)
    if gender in dict(Product.GENDER_CHOICES):
        products = products.filter(gender=gender)
    if stock_filter == "low":
        products = products.filter(stock__lte=5)
    elif stock_filter == "out":
        products = products.filter(stock=0)

    paginator = Paginator(products.order_by("-created_at"), 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "dashboard/product_list.html",
        {
            "page_obj": page_obj,
            "q": q,
            "status": status,
            "gender": gender,
            "stock_filter": stock_filter,
            "gender_choices": Product.GENDER_CHOICES,
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"✨ '{product.name_uz}' atiri katalogga muvaffaqiyatli qo'shildi.")
        return redirect("dashboard:product_list")
    return render(request, "dashboard/product_form.html", {"form": form, "title": "Yangi atir qo'shish"})


@staff_required
@require_http_methods(["GET", "POST"])
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"✨ '{product.name_uz}' ma'lumotlari saqlandi.")
        return redirect("dashboard:product_list")
    return render(
        request,
        "dashboard/product_form.html",
        {"form": form, "product": product, "title": f"'{product.name_uz}'ni tahrirlash"},
    )


@staff_required
@require_http_methods(["POST"])
def product_toggle_active(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save()
    state_str = "faollashtirildi" if product.is_active else "yashirildi"
    messages.success(request, f"'{product.name_uz}' mahsuloti {state_str}.")
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer if referer else "dashboard:product_list")


@staff_required
@require_http_methods(["POST"])
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product_name = product.name_uz
    product.delete()
    messages.success(request, f"🗑️ '{product_name}' katalogdan o'chirildi.")
    return redirect("dashboard:product_list")


@staff_required
def order_list(request):
    orders = Order.objects.prefetch_related("items")
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    status_counts = dict(Order.objects.values("status").annotate(total=Count("id")).values_list("status", "total"))
    total_orders_count = Order.objects.count()

    if q:
        orders = orders.filter(Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(telegram_username__icontains=q))
    if status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)

    paginator = Paginator(orders.order_by("-created_at"), 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "dashboard/order_list.html",
        {
            "page_obj": page_obj,
            "q": q,
            "status": status,
            "status_choices": Order.STATUS_CHOICES,
            "status_counts": status_counts,
            "total_orders_count": total_orders_count,
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=pk)
    form = OrderStatusForm(request.POST or None, instance=order)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"⚡ Buyurtma #{order.pk} holati '{order.get_status_display()}'ga o'zgartirildi.")
        return redirect("dashboard:order_detail", pk=order.pk)
    return render(
        request,
        "dashboard/order_detail.html",
        {
            "order": order,
            "form": form,
            "status_choices": Order.STATUS_CHOICES,
        },
    )


@staff_required
@require_http_methods(["POST"])
def order_quick_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get("status")
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        messages.success(request, f"⚡ Buyurtma #{order.pk} statusi '{order.get_status_display()}'ga yangilandi.")
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer if referer else "dashboard:order_list")


@staff_required
def order_receipt(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=pk)
    return render(request, "dashboard/order_receipt.html", {"order": order})


@staff_required
@require_http_methods(["GET", "POST"])
def site_settings_view(request):
    settings_obj = SiteSettings.get_settings()
    form = SiteSettingsForm(request.POST or None, request.FILES or None, instance=settings_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✨ Sayt sozlamalari va rasmlari muvaffaqiyatli saqlandi.")
        return redirect("dashboard:settings")
    return render(request, "dashboard/settings.html", {"form": form, "settings_obj": settings_obj})

