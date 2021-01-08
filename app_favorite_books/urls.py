from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('books', views.show_all_books),
    path('addFavoriteBook', views.add_favorite_book),
    path('books/<int:book_id>', views.show_favorite_book), # show fave book info --- PASS BOOK ID
    path('addToFavorites/<int:book_id>', views.add_to_favorites),
    path('unfavorite/<int:book_id>', views.unfavorite),
    # path('editBook', views.edit_book),
    # path('deleteBook', views.delete_book),
    path('logout', views.logout)
]