from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Product, Order, OrderItem

def _cart(request):
    return request.session.setdefault("cart", {})

def _cart_details(request):
    cart = request.session.get("cart", {})
    rows, total, count = [], Decimal("0.00"), 0
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id), is_active=True)
        except (Product.DoesNotExist, ValueError):
            continue
        quantity = max(1, min(int(quantity), product.stock or 1))
        line_total = product.price * quantity
        rows.append({"product": product, "quantity": quantity, "line_total": line_total})
        total += line_total
        count += quantity
    return rows, total, count

def home(request):
    products = Product.objects.filter(is_active=True)
    category = request.GET.get("category", "").strip()
    query = request.GET.get("q", "").strip()
    if category:
        products = products.filter(category__iexact=category)
    if query:
        products = products.filter(name__icontains=query)
    categories = Product.objects.filter(is_active=True).values_list("category", flat=True).distinct()
    return render(request, "store/home.html", {
        "products": products, "categories": categories, "selected_category": category, "query": query
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "store/product_detail.html", {"product": product})

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = request.session.get("cart", {})
    current = int(cart.get(str(product_id), 0))
    if product.stock > current:
        cart[str(product_id)] = current + 1
        request.session["cart"] = cart
        messages.success(request, f"{product.name} added to your cart.")
    else:
        messages.warning(request, "Sorry, there isn't enough stock available.")
    return redirect(request.POST.get("next") or "cart")

def cart_view(request):
    rows, total, count = _cart_details(request)
    return render(request, "store/cart.html", {"cart_items": rows, "total": total, "cart_count": count})

@require_POST
def update_cart(request, product_id):
    cart = request.session.get("cart", {})
    key = str(product_id)
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        quantity = 1
    if quantity <= 0:
        cart.pop(key, None)
    elif quantity <= product.stock:
        cart[key] = quantity
    else:
        messages.warning(request, f"Only {product.stock} item(s) are available.")
        cart[key] = product.stock
    request.session["cart"] = cart
    return redirect("cart")

@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    messages.info(request, "Item removed from your cart.")
    return redirect("cart")

@login_required
def checkout(request):
    rows, total, count = _cart_details(request)
    if not rows:
        messages.info(request, "Your cart is empty.")
        return redirect("home")
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()
        if not all([full_name, email, address]):
            messages.error(request, "Please complete all checkout fields.")
            return render(request, "store/checkout.html", {"cart_items": rows, "total": total})
        with transaction.atomic():
            # Re-check inventory at order time to avoid overselling.
            for row in rows:
                product = Product.objects.select_for_update().get(pk=row["product"].pk)
                if product.stock < row["quantity"]:
                    messages.error(request, f"Not enough stock for {product.name}. Please update your cart.")
                    return redirect("cart")
            order = Order.objects.create(user=request.user, full_name=full_name, email=email, address=address, total=total)
            for row in rows:
                product = Product.objects.select_for_update().get(pk=row["product"].pk)
                OrderItem.objects.create(order=order, product=product, product_name=product.name,
                                         unit_price=product.price, quantity=row["quantity"])
                product.stock -= row["quantity"]
                product.save(update_fields=["stock"])
        request.session["cart"] = {}
        messages.success(request, f"Order #{order.pk} placed successfully. Demo checkout uses cash on delivery.")
        return redirect("order_history")
    return render(request, "store/checkout.html", {"cart_items": rows, "total": total})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "store/orders.html", {"orders": orders})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "store/register.html", {"form": form})
