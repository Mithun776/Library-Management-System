from distutils.command import upload
from webbrowser import get
from django.db import models
from django.utils import timesince
from datetime import datetime, timedelta, date
from simple_history.models import HistoricalRecords
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, AbstractUser, BaseUserManager


def get_expiry():
    return datetime.today() + timedelta(days=15)


def get_expiry_staff():
    return datetime.today() + timedelta(days=60)


class Book(models.Model):
    class Program(models.TextChoices):
        UG = 'UG'
        PG = 'PG'

    class Status(models.TextChoices):
        AVAILABLE = 'available'
        ISSUED = 'issued'
        UNAVAILABLE = 'unavailable'
        ERROR = 'error! please check'

    name = models.CharField(max_length=2000)
    isbn = models.IntegerField(default=None)
    publisher = models.CharField(max_length=4000, default=None)
    access_code = models.IntegerField(default=None, primary_key=True)
    course = models.CharField(max_length=10, choices=Program.choices, default=Program.UG)
    edition = models.IntegerField(default=None, blank=True, null=True)
    author = models.CharField(max_length=200, default=None)
    status = models.CharField(max_length=200, choices=Status.choices, default="available")
    # volume = models.ForeignKey("Book_Copies", on_delete=models.CASCADE, related_name='book_copies', default=None, blank=True, null=True)
    category = models.CharField(max_length=2000, default=None, blank=True)
    issue_date = models.DateField(default=None, null=True, blank=True)
    ret_date = models.DateField(default=None, null=True, blank=True)
    issue_to = models.ForeignKey("Users", on_delete=models.SET_NULL, null=True, blank=True, related_name='books', to_field='id_number')
    reference = models.BooleanField(default=False, null=True, blank=True)
    purchase_date = models.DateField(default=None, blank=True, null=True)
    cost = models.IntegerField(default=None, blank=True, null=True)
    pub_year = models.IntegerField(default=None, blank=True, null=True)
    history = HistoricalRecords()
    
    def __str__(self):
        #print(f"accession code: {self.access_code}; Book: {self.name} || ISBN: {self.isbn} edition: {self.edition}|| Author: {self.author} || volumes: {self.copies.all()} || category: {self.category} || ID: {self.issue_to.id_number},{self.issue_to.name} || From: {self.issue_date} || Till: {self.ret_date})")
        return f"access code: {self.access_code} || Book: {self.name} || ISBN: {self.isbn} || From: {self.issue_date} || Till: {self.ret_date} || status: {self.status}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        permissions = [
            ('only_view_book', 'Only View Book'),
            ('edit_only_book', 'Edit Only Book'),
            ('add_only_book', 'Add Only Book'),
        ]


class Book_Copies(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    total_copies = models.IntegerField(default=0)
    issued_copies = models.IntegerField(default=0)
    available_copies = models.IntegerField(default=0)

    def __str__(self):
        return f"Book: {self.book} || Total Copies: {self.total_copies} || Issued Copies: {self.issued_copies} || Available Copies: {self.available_copies}"


class TransactionLog(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField(default=0, null=True, blank=True)
    transaction_type = models.CharField(max_length=200)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user} || Transaction Type: {self.transaction_type} || Transaction Date: {self.transaction_date}"


class Magazine(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200, default=None, blank=True)    
    author = models.CharField(max_length=200, default=None)
    isbn = models.IntegerField(default=None)
    edition = models.CharField(max_length=200, default=None)
    publisher = models.CharField(max_length=400, default=None, blank=True, null=True)
    access_code = models.IntegerField(default=0, primary_key=True)
    cost = models.IntegerField(default=None, blank=True, null=True)

    def __str__(self):
        return f"Magazine: {self.name}; access_code: {self.access_code} ; ISBN: {self.isbn} ; Author: {self.author} ;edition : {self.edition}"

    class Meta:
        permissions = [
            
            ('only_view_magazine', 'Only View Magazine'),
            ('edit_only_magazine', 'Edit Only Magazine'),
            ('add_only_magazine', 'Add Only Magazine'),
        ]


class File(models.Model):
    file = models.FileField(upload_to='files/', blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='files')
    date_uploaded = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    history = HistoricalRecords()
    def __str__(self):
        return f"File: {self.file} ; Title: {self.title} ; Description: {self.description} ; Staff: {self.user} ;"
    
    def save(self, *args, **kwargs):
        """
        if self.user.user_type != 2 or self.user.user_type != 1:
            raise ValueError("Only staff and librarian can upload files")
        super().save(*args, **kwargs)
        """
        if self.user:
            self.user.save()
        super().save(*args, **kwargs)

    class Meta:
        permissions = [
            ('only_view', 'Only View'),
            ('add', 'Add'),
            ('delete', 'Delete'),
        ]       


class Holidays(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"Date: {self.date} ; Name: {self.name} ;"


class Notification(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    user = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        issued_books = extra_fields.pop('issued_book', None)
        if issued_books is not None:
            user.issued_book.set(issued_books)

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 1)
        extra_fields.setdefault('name', 'admin')
        extra_fields.setdefault('phone', '1234567890')
        extra_fields.setdefault('id_number', 'admin')
        extra_fields.setdefault('fine', 0)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, email, password, **extra_fields)


class Message(models.Model):
    sender = models.ForeignKey("Users", related_name='sender', on_delete=models.CASCADE)
    # owner = models.ForeignKey("Users", related_name='owner', on_delete=models.CASCADE)
    content = models.TextField()
    subject = models.TextField(default=None, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class FaceAttendance(models.Model):

    user_info = models.ForeignKey('Users', on_delete=models.CASCADE)
    last_attendance = models.TextField()
    total = models.IntegerField(default=0)
    status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.user_info.id_number} {self.last_attendance} {self.total}'


class AttendanceHistory(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"User: {self.user} ; Date: {self.date} ; Status: {self.status} ;"


class Users(AbstractUser):
    USER_TYPE_CHOICES = (
      (1, 'librarian'),
      (2, 'staff'),
      (3, 'student'),
      (4, 'library_staff')
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=10)
    fine = models.IntegerField(default=0)
    issued_book = models.ManyToManyField(Book, blank=True, related_name='users_books')
    id_number = models.CharField(max_length=200, primary_key=True)
    attendance = models.ForeignKey(FaceAttendance, on_delete=models.CASCADE, blank=True, null=True)
    objects = UserManager()
    history = HistoricalRecords()

    def __str__(self):
        return f"Name: {self.name} ; ID: {self.id_number} type: {self.user_type}; password: {self.password} ;Email: {self.email} ; Phone: {self.phone} ; Fine: {self.fine} ; issued book: {self.issued_book} ;"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
               
        if self.issued_book:
            for book in self.issued_book.all():
                if book is None:
                    b = Book.objects.get(name='sample')
                    book = b
            """
                if self.user_type == 3:
                    if book.issue_date:
                        book.issue_date = datetime.today()
                        book.ret_date = get_expiry()
                        book.save()
                        super().save(*args, **kwargs)
                        self.fine = fine(book.ret_date)
                if self.user_type == 2:
                    if book.issue_date:
                        book.issue_date = datetime.today()
                        book.ret_date = get_expiry_staff()
                        book.save()
                        super().save(*args, **kwargs)
                        self.fine = fine(book.ret_date)
                super().save(*args, **kwargs)
    """
    class Meta:
        permissions = [
            ("librarian", "Librarian"),
        ]
