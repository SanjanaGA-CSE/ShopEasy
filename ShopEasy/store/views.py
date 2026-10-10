import json
from decimal import Decimal

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .forms import RegisterForm
from .models import Order, OrderItem, Product


def home(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    return render(request, "index.html", {"products": products, "query": query})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "product.html", {"product": product})


@ensure_csrf_cookie
def cart(request):
    # The cart itself lives in the browser (localStorage); see static/js/script.js.
    return render(request, "cart.html")


def _error(message, status=400):
    return JsonResponse({"error": message}, status=status)


@require_POST
def checkout(request):
    if not request.user.is_authenticated:
        return _error("Please log in to place your order.", status=401)

    try:
        items = json.loads(request.body)["items"]
    except (ValueError, KeyError, TypeError):
        return _error("Invalid cart data.")

    if not isinstance(items, list) or not items:
        return _error("Your cart is empty.")

    # Validate what the browser sent. Never trust prices from the client.
    wanted = {}
    for entry in items:
        try:
            product_id = int(entry["id"])
            quantity = int(entry["quantity"])
        except (KeyError, ValueError, TypeError):
            return _error("Invalid cart item.")
        if quantity < 1 or quantity > 1000:
            return _error("Invalid quantity.")
        wanted[product_id] = wanted.get(product_id, 0) + quantity

    with transaction.atomic():
        products = {
            p.id: p for p in Product.objects.select_for_update().filter(id__in=wanted)
        }
        if len(products) != len(wanted):
            return _error("One or more products are no longer available.")

        for product_id, quantity in wanted.items():
            product = products[product_id]
            if product.stock < quantity:
                return _error(f"Only {product.stock} left of {product.name}.")

        order = Order.objects.create(
            customer=request.user, total=Decimal("0.00"), status=Order.CONFIRMED
        )
        total = Decimal("0.00")
        for product_id, quantity in wanted.items():
            product = products[product_id]
            # Price comes from the database, not from the browser.
            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=product.price
            )
            product.stock -= quantity
            product.save(update_fields=["stock"])
            total += product.price * quantity
        order.total = total
        order.save(update_fields=["total"])

    return JsonResponse(
        {"order_id": order.id, "redirect": reverse("order_success", args=[order.id])}
    )


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    return render(request, "order_success.html", {"order": order})


@login_required
def my_orders(request):
    orders = request.user.orders.prefetch_related("items__product")
    return render(request, "my_orders.html", {"orders": orders})


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})
