from django.db import models
import re
import bcrypt

class UserManager(models.Manager):
    def validate_registration(self, postData):
        errors = {}

        if len(postData['first_name']) < 2:
            errors['first_name'] = "First name must be at least 2 characters."

        if len(postData['last_name']) < 2:
            errors['last_name'] = "Last name must be at least 2 characters."

        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):    # test whether a field matches the pattern
            errors['email'] = "Invalid email address!"

        # if same email is found in db, show error
        user = User.objects.filter(email=postData['email'])
        if len(user) > 0:
            print("Email already exists!")
            errors['email'] = "Email already exists."

        if postData['password'] != postData['confirm_password']:
            errors['password'] = "Passwords don't match!"
        elif len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 characters."

        return errors




    def validate_login(self, postData):
        errors = {}

        user = User.objects.filter(email=postData['login_email'])

        if len(User.objects.filter(email=postData['login_email'])) == 0:
            print("User was not found!")
            errors['login_email'] = "Email was not found, please register."
        else:
            if not bcrypt.checkpw(postData['login_password'].encode(), user[0].password.encode()):
                print("Passwords DON'T match!")
                errors['login_password'] = "Password was incorrect!"

        return errors




class BookManager(models.Manager):
# title is required
# desc must be at least 5 char
    def validate_book(self, postData):
        errors = {}
        # check if book is in db already
        title = postData['title'].strip() # will eliminate spaces in front & back of title
        desc = postData['desc'].strip()
        book = Book.objects.filter(title=title)


        if len(book) > 0:
            errors['title'] = "Book is already in our list of favorite books!"
        if len(title) == 0:
            errors['title'] = "Please include a book title."
        if len(desc) < 5:
            errors['desc'] = "Book description must be at least 5 characters."
        return errors



class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # liked_books = LIST of books a user likes
    # books_uploaded = LIST of books uploaded by a user
    objects = UserManager()

class Book(models.Model):
    title = models.CharField(max_length=255)
    desc = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, related_name="books_uploaded", on_delete = models.CASCADE)
    # one-to-many relationship because a user can upload many books, and a book can be uploaded by one user.
    # uploaded_by === the user tho uploaded the book
        users_who_like = models.ManyToManyField(User, related_name="liked_books")
    # many-to-many relationship, where a given user can like many books, and a given book can be liked by many users
    # a LIST of users who like a specific book
    objects = BookManager()