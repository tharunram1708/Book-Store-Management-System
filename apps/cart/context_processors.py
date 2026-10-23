from django.db.models import Sum
from .models import CartItem


def cart_summary(request):
    if not request.user.is_authenticated:
        return {"cart_item_count": 0}
    result = CartItem.objects.filter(cart__user=request.user).aggregate(count=Sum("quantity"))
    return {"cart_item_count": result["count"] or 0}
