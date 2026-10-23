from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [path("admin/", admin.site.urls), path("accounts/", include("apps.accounts.urls")),
               path("books/", include("apps.books.urls")), path("categories/", include("apps.categories.urls")),
               path("cart/", include("apps.cart.urls")), path("orders/", include("apps.orders.urls")),
               path("", include("apps.dashboard.urls"))]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
