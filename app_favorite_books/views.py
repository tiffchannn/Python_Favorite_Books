from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import User, Book
import bcrypt

def index(request):
    print('this is from index!')
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        errors = User.objects.validate_registration(request.POST)

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        form_password = request.POST['password']
        pw_hash = bcrypt.hashpw(form_password.encode(), bcrypt.gensalt()).decode()

        created_user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            password = pw_hash
            )

        request.session['user_id'] = created_user.id

        messages.success(request, "Registration was successful, please login!")
        return redirect('/')

def login(request):
    if request.method == 'POST':
        errors = User.objects.validate_login(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        else:
            user = User.objects.get(email=request.POST['login_email'])
            request.session['user_id'] = user.id

            print('User ID:', user.id)
            return redirect('/books')

def show_all_books(request):
# get all books from db, use context
# get all favorited books by user - this will help display on all_books.html if this book is faved or not

    if 'user_id' not in request.session:
        messages.error(request, "Please log in!")
        return redirect('/')

    user = User.objects.get(id=request.session['user_id'])
    favorite_books = user.liked_books.all() # get all books from user

    context = {
        'all_books': Book.objects.all(),
        'favorite_books': favorite_books,
        'logged_user': User.objects.get(id=user.id)
    }

    print(context['favorite_books'])

    print('this is coming from show all books')
    return render(request, 'dashboard.html', context)

def add_favorite_book(request):
    # add a new book, with validations. Added books should automatically be favorited by the logged in user.

    errors = Book.objects.validate_book(request.POST)
    user = User.objects.get(id=request.session['user_id'])

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/books')
    else:
        form_title = request.POST['title']
        form_desc = request.POST['desc']
        book = Book.objects.create(title=form_title, desc=form_desc, uploaded_by=user) # creates book
        print("Book ID: " + str(book.id))
        user.liked_books.add(book.id) #favorites the book that was just created
        # book.users_who_like.add(user.id)
        # for user in book.users_who_like.all()
        #     user.first_name
    print('*'*70)
    print('this is from add favorite book --- ')
    print('New Book Added: ', request.POST)
    return redirect('/books')


def show_favorite_book(request, book_id):
# display specifc FAVORITE book (pull book id)
# show users who have faved this book
# if user is logged in, can make edits
    user = User.objects.get(id=request.session['user_id'])
    book = Book.objects.get(id=book_id)
    favorite_books = user.liked_books.all()

    if request.method == 'GET':
        print('this is coming from show favorite book: ' + str(id))
        context = {
            'book': Book.objects.get(id=book_id),
            'logged_user': User.objects.get(id=user.id),
            'users_who_like': Book.objects.get(id=book_id).users_who_like.all(),
            'favorite_books': favorite_books
        }
        if book not in user.liked_books.all():
            return render(request, 'book_info.html', context)
        else:
            return render(request, 'favorite_book.html', context)


    if request.method == 'POST':
        # process the form
        book = Book.objects.get(id=book_id)
        if (request.POST['button'] == 'Update'):
            print('this is updating id: ' + str(id))
            #redirect to same page
            errors = Book.objects.validate_book(request.POST)
            user = User.objects.get(id=request.session['user_id'])

            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value)
                return redirect(f'/books/{book_id}')
            else:
                book_to_update = Book.objects.get(id=book_id)
                book_to_update.title = request.POST['title'].strip()
                book_to_update.desc = request.POST['desc'].strip()
                book_to_update.save()

                print('Book was updated!', request.POST)
                return redirect('/books')

        elif (request.POST['button'] == 'Delete'):
            print('this is deleting id: ' + str(id))

            book_to_delete = Book.objects.get(id=book_id)
            book_to_delete.delete()
            print('This book was deleted!')
            return redirect('/books')


def show_book_info(request, book_id):
#display specific book which is NOT a favorite
    user = User.objects.get(id=request.session['user_id'])
    context = {
        'book': Book.objects.get(id=book_id),
        'logged_user': User.objects.get(id=user.id),
        'users_who_like': Book.objects.get(id=book_id).users_who_like.all(),
    }

    print('Users Who Like this Book:', Book.objects.first().users_who_like.all())

    print('this is from show book info')
    return render(request, 'book_info.html', context)



def add_to_favorites(request, book_id):
    user = User.objects.get(id=request.session['user_id'])
    book = Book.objects.get(id=book_id)

    if book not in user.liked_books.all():
        #add book to favorites
        user.liked_books.add(book.id)

    print('Book was added to favorites')
    return redirect(f'/books/{book_id}')

def unfavorite(request, book_id):
    user = User.objects.get(id=request.session['user_id'])
    book = Book.objects.get(id=book_id)

    if book in user.liked_books.all():
        user.liked_books.remove(book.id)

    print('This book was removed from liked books.' + str(book.id))
    return redirect(f'/books/{book_id}')

def logout(request):
    request.session.clear()

    print("Logged Out!")
    messages.success(request, "You have been logged out!")
    return redirect('/')


# ----- HOW TO GRAB FAVORITES FROM DB -------
# select from favorites where book_id matches id from url AND user id matches url id of logged in user --> then show specific template