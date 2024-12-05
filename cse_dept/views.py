import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, fields
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.models import Permission
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Book, Users, Magazine, File, Notification, Book_Copies, TransactionLog,Message, FaceAttendance, AttendanceHistory
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
# from .forms import Login
from .forms import SearchForm, BookForm, MagForm, addMagazine, UserForm
from datetime import date, datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from email.message import EmailMessage
from django.contrib.auth.decorators import permission_required
from .decorators import group_required
from django.contrib.auth.models import Group
from .serializers import UsersSerializer
from django.core.paginator import Paginator


def calculate_days(date1, date2):
    if date1 is None or date2 is None:
        raise ValueError("Both date1 and date2 must be valid dates")
    delta = date2() - date1
    return delta.days


def nearest_date(isbn):
    current_date = date.today()

    # Query the database to get all books with the same ISBN and calculate the difference with the current date
    books = Book.objects.filter(isbn=isbn).annotate(
        ret_date_difference=ExpressionWrapper(
            F('ret_date') - current_date,
            output_field=fields.DurationField()
        )
    )

    # Get the book with the smallest ret_date difference
    nearest_ret_date_book = books.order_by('ret_date_difference').first()
    print(nearest_ret_date_book)
    return nearest_ret_date_book.ret_date


def login_user(request):
    if request.method == 'POST':
        id_number = request.POST['usn']
        password = request.POST['password']
        user = authenticate(request, username=id_number, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == 1:
                return redirect('librarian')
            elif user.user_type == 2:
                return redirect('staff_dashboard', id=user.id_number)
            else:
                return redirect('student', id=user.id_number)
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login_user')        
    return render(request, 'login.html', {})


"""
@login_required()
@group_required('librarian')
def get_user_details(request, id):
    u = Users.objects.get(id_number=id)
    issued_books = u.issued_book.all()  # Retrieve the issued books for the user
    book_list = []
    for book in issued_books:
        book_list.append({
            'id': book.access_code,
            'name': book.name,
            'isbn': book.isbn,
            'edition': book.edition,
            'author': book.author,
            'issue_date': book.issue_date,
            'available_on': book.ret_date,
        })
    context = {
        'name': u.name,
        'phone': u.phone,
        'usn': u.id_number,
        'email': u.email,
        'fine': u.fine,
        'issued': book_list,
    }
    return JsonResponse(context)
"""


@login_required()
@group_required('student')
def student(request, id):
    u = get_object_or_404(Users, id_number=id)
    issued_books = u.issued_book.all()  # Retrieve the issued books for the user
    book_list = []
    for book in issued_books:
        book_list.append({
             'id': book.access_code,
                'name': book.name,
                'isbn': book.isbn,
                'edition': book.edition,
                'author': book.author,
                'issue_date': book.issue_date,
                'available_on': book.ret_date,
        })
    context = {
            'name': u.name,
            'phone': u.phone,
            'usn': u.id_number,
            'email': u.email,
            'fine': u.fine,
            'issued': book_list,
        }
    return render(request, 'user.html', context)


@login_required()
@group_required('staff')
def staff_about(request, id):
    u = get_object_or_404(Users, id_number=id)
    issued_books = u.issued_book.all()
    book_list = []
    for book in issued_books:
        book_list.append({
            'id': book.access_code,
            'name': book.name,
            'isbn': book.isbn,
            'edition': book.edition,
            'author': book.author,
            'issue_date': book.issue_date,
            'available_on': book.ret_date,
        })
    context = {
        'name': u.name,
        'phone': u.phone,
        'usn': u.id_number,
        'email': u.email,
        'fine': u.fine,
        'issued': book_list,
    }
    messages.success(request, 'you have logged in...')
    return render(request, 'user.html', context)


@login_required()
@permission_required('librarian')
def librarian(request):
    return render(request, 'librarian.html', {})


@login_required()
@permission_required('librarian')
def lib_book(request):
    total = Book.objects.all().count()
    issued_total = Book.objects.filter(status='issued').count()
    if request.method == 'POST':
        query = request.POST.get('query')
        results = Book.objects.filter(Q(name__icontains=query) | Q(isbn__icontains=query) | Q(access_code__icontains=query))
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        lis = []
        for i in results:
            lis.append({
                'id': i.access_code,
                'name': i.name,
                'isbn': i.isbn,
                'status': i.status,
                'edition': i.edition,
                'author': i.author,
                'copies': [copy.total_copies for copy in i.copies.all()],
                'available': [copy.available_copies for copy in i.copies.all()],
                'reference': i.reference,
                'issue_date': i.issue_date,
                'available_on': i.ret_date,
            })
        return render(request, 'lib_book.html', {'list': lis, 'page_obj': page_obj, 'total': total, 'issued': issued_total})
    else:
        obj = Book.objects.order_by('isbn', 'name').annotate()
        #obj = Book.objects.order_by('isbn', 'name').distinct('isbn')  # use progresql for distinct('isbn')
        paginator = Paginator(obj, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        lis = []
        for i in obj:
            lis.append({
                'id': i.access_code,
                'name': i.name,
                'isbn': i.isbn,
                'edition': i.edition,
                'author': i.author,
                'copies': [copy.total_copies for copy in i.copies.all()],
                'available': [copy.available_copies for copy in i.copies.all()],
                'reference': i.reference,
                'issue_date': i.issue_date,
                'available_on': i.ret_date,
            })
        print(lis)
        return render(request, "lib_book.html", {'list': lis, 'page_obj': page_obj, 'total': total, 'issued': issued_total})


@login_required()
@permission_required('librarian')
def lib_mag(request):
    obj = Magazine.objects.all()
    lis = []
    for i in obj:
        lis.append({
            'id': i.access_code,
            'name': i.name,
            'isbn': i.isbn,
            'author': i.author,
            'category': i.category,
            'edition': i.edition,
        })
    print(lis)
    return render(request, "lib_mag.html", {'list': lis})


# depreciated function
"""
@login_required()
@permission_required('librarian')
def lib_staff(request):
    lis = []
    if request.method == 'POST':
        query = request.POST.get('query')
        results = Users.objects.filter(id_number__icontains=query)
        for i in results:
            if i.issued_book.all():
                for book in i.issued_book.all():
                    lis.append({
                        'id': i.id_number,
                        'name': i.name,
                        'staff_id': i.id_number,
                        'email': i.email,
                        'phone': i.phone,
                        'fine': i.fine,
                        'issued_book': book,
                        'ret_date': book.ret_date,
                        #'issued_reference': i.issued_reference,
                        })
            else:
                lis.append({
                    'id': i.id_number,
                    'name': i.name,
                    'staff_id': i.id_number,
                    'email': i.email,
                    'phone': i.phone,
                    'fine': i.fine,
                    'issued_book': None,
                })
        return render(request, 'lib_staff.html', {'results': lis})
    else:
        obj = Users.objects.filter(user_type=2)
        for i in obj:
            if i.issued_book.all():
                for book in i.issued_book.all():
                    lis.append({
                        'id': i.id_number,
                        'name': i.name,
                        'staff_id': i.id_number,
                        'email': i.email,
                        'phone': i.phone,
                        'fine': i.fine,
                        'issued_book': book,
                        'ret_date': book.ret_date,
                        #'issued_reference': i.issued_reference,
                        })
            else:
                lis.append({
                    'id': i.id_number,
                    'name': i.name,
                    'staff_id': i.id_number,
                    'email': i.email,
                    'phone': i.phone,
                    'fine': i.fine,
                    'issued_book': None,
                })
    print(lis)
    return render(request, "lib_staff.html", {'list': lis})
"""


@login_required()
@permission_required('librarian')
def lib_student(request):
    lis = []
    total = Users.objects.all().count() - 1
    if request.method == 'POST':
        query = request.POST.get('query')
        results = Users.objects.filter(Q(id_number__icontains=query) | Q(name__icontains=query))
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        for i in results:
            if i.issued_book.all():
                ret_dates = [f"book-{index+1}: " + book.ret_date.strftime('%d-%m-%Y') for index, book in enumerate(i.issued_book.all())]
                book = ["book: " + book.name + " | " + "code: " + str(book.access_code) for book in i.issued_book.all()]
                lis.append({
                    'id': i.id_number,
                    'name': i.name,
                    'usn': i.id_number,
                    'email': i.email,
                    'phone': i.phone,
                    'fine': i.fine,
                    'issued_book': book,
                    'ret_date': ret_dates,
                })
            else:
                lis.append({
                    'id': i.id_number,
                    'name': i.name,
                    'usn': i.id_number,
                    'email': i.email,
                    'phone': i.phone,
                    'fine': i.fine,
                    'issued_book': None,
                    })
        return render(request, 'lib_user.html', {'results': lis, 'page_obj': page_obj, 'total': total})
    
    else:
        obj = Users.objects.filter(Q(user_type=3) | Q(user_type=2))
        paginator = Paginator(obj, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        for i in obj:
            if i.issued_book.all():
                ret_dates = [f"book-{index + 1}: " + book.ret_date.strftime('%d-%m-%Y') + " | " for index, book in enumerate(i.issued_book.all())]
                book = [f"book-{index+1}: " + book.name + " | " + "code: " + str(book.access_code) for index, book in enumerate(i.issued_book.all())]
                lis.append({
                    'id': i.id_number,
                    'name': i.name,
                    'usn': i.id_number,
                    'email': i.email,
                    'phone': i.phone,
                    'fine': i.fine,
                    'issued_book': book,
                    'ret_date': ret_dates,
                })

            else:
                lis.append({
                    'id': i.id_number,
                    'name': i.name,
                    'usn': i.id_number,
                    'email': i.email,
                    'phone': i.phone,
                    'fine': i.fine,
                    'issued_book': None,
                    })
    
    print(lis)
    return render(request, "lib_user.html", {'list': lis, 'page_obj': page_obj, 'total': total})


@login_required()
@permission_required('librarian')
def lib_auto(request):
    students = Users.objects.filter(user_type=3)
    for student in students:
        if student.fine > 0:
            subject = 'Fine payment'
            body = f"Please pay your fine of Rs. {student.fine} as soon as possible."
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [student.email],
            )
    staffs = Users.objects.filter(user_type=2)
    for staff in staffs:
        if staff.fine > 0:
            subject = 'Fine payment'
            body = f"Please pay your fine of Rs. {staff.fine} as soon as possible."
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [staff.email],
            )
    return render(request, 'lib_auto.html', {})


@login_required()
@permission_required('librarian')
def lib_issue(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        access_code = request.POST.get('access_code')
        ret = request.POST.get('return_date')

        print(id, access_code)
        book = Book.objects.filter(access_code=access_code).first()
        book_copy = Book_Copies.objects.get(book=book)
        user = Users.objects.filter(id_number=id).first()
        if user and book and book_copy:
            if user.user_type == 3:
                if book.status == 'issued':
                    messages.error(request, 'Book already issued')
                    return redirect('lib_issue')
                if Book.objects.filter(issue_to=user, access_code=access_code).exists():
                    messages.error(request, 'This book is already issued to the student')
                    return redirect('lib_issue')
                if user.issued_book.all().count() >= 3:
                    messages.error(request, 'User can issue only 3 books')
                    return redirect('lib_issue')
                if book_copy.available_copies == 0:
                    messages.error(request, 'Book not available')
                    return redirect('lib_issue')
                if book.status == 'available':
                    if user.fine == 0:
                        user.issued_book.add(book)
                    else:
                        messages.error(request, 'User has fine of Rs.'+str(user.fine))
                        return redirect('lib_issue')
                    if ret:
                        book.ret_date = ret
                    else:
                        book.ret_date = date.today() + timedelta(days=15)
                    book.issue_to = user
                    book.issue_date = date.today()
                    book.status = 'issued'
                    TransactionLog.objects.create(user=user, transaction_type=f'issue of book:{book.access_code}')
                    #book.copies -= 1
                    user.save()
                    book.save()
                    context = {
                            'name': user.name,
                            'book': book.name,
                            'issue_date': book.issue_date,
                            'return_date': book.ret_date,
                            }
                    messages.success(request, 'Book issued successfully')
                    return render(request, 'lib_issue.html', context)
            
            if user.user_type == 2:
                if book.status == 'issued':
                    messages.error(request, 'Book already issued')
                    return redirect('lib_issue')
                if user.issued_book.filter(access_code=access_code).exists():
                    messages.error(request, 'This book is already issued to the staff')
                    return redirect('lib_issue')
                if user.issued_book.count() >= 5:
                    messages.error(request, 'User can issue only 5 books')
                    return redirect('lib_issue')
                if book and book_copy.available_copies == 0:
                    messages.error(request, 'Book not available')
                    return redirect('lib_issue')

                if book.status == 'available':
                    if user.fine > 0:
                        messages.error(request, 'You have fine of Rs.'+str(user.fine))
                        return redirect('lib_issue')
                    else:
                        user.issued_book.add(book)
                        if ret:
                            book.ret_date = ret
                        else:
                            book.ret_date = date.today() + timedelta(days=60)
                        book.issue_date = date.today()
                        book.issue_to = user
                        book.status = 'issued'

                        # book.copies -= 1
                        user.save()
                        book.save()
                        context = {
                            'name': user.name,
                            'book': book.name,
                            'issue_date': book.issue_date,
                            'return_date': book.ret_date,
                        }
                        TransactionLog.objects.create(user=user, transaction_type=f'issue of book:{book.access_code}')
                        messages.success(request, 'Book issued successfully')
                        return render(request, 'lib_issue.html', context)
        else:
            messages.error(request, 'Invalid ID')
            return redirect('lib_issue')
    return render(request, 'lib_issue.html', {})


@login_required()
@permission_required('librarian')
def lib_return(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        access_code = request.POST.get('access_code')
        print(id, access_code)
        book = Book.objects.get(access_code=access_code)
        book_copy = Book_Copies.objects.get(book=book)
        user = Users.objects.get(id_number=id)
        prev_issue_date = book.issue_date
        prev_return_date = book.ret_date
        if user and book and book_copy:
            if user.issued_book.filter(access_code=access_code).exists():
                # depreciated fxn calculate fine when returning
                """
                issue_date = book.issue_date
                return_date = date.today
                days = calculate_days(issue_date, return_date)
                if user.user_type == '3' and days > 15:
                    user.fine += (days - 15) * 5
                elif user.user_type == '2' and days > 60:
                    user.fine += (days - 60) * 5
                user.save()
                """
                if user.fine > 0:
                    messages.error(request, 'Fine of Rs.'+str(user.fine))
                    return redirect('lib_return')
                user.issued_book.remove(book)
                book.issue_to = None
                book.issue_date = None
                book.ret_date = None
                book.status = 'available'
                TransactionLog.objects.create(user=user, transaction_type=f'return of book:{book.access_code}')
                # book.copies += 1
                user.save()
                book.save()
                context = {
                    'name': user.name,
                    'book': book.name,
                    'issue_date': prev_issue_date,
                    'return_date': prev_return_date,
                    'fine': user.fine,
                }
                messages.success(request, 'Book returned successfully')
                return render(request, 'lib_return.html', context)
            else:
                messages.error(request, "Invalid, no book issued")
                return redirect('lib_return')
        else:
            messages.error(request, 'Invalid ID')
            return redirect('lib_return')
    return render(request, 'lib_return.html', {})


@login_required()
@permission_required('librarian')
def repay_due(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        amount = request.POST.get('amount')
        user = Users.objects.filter(id_number=id).first()
        if user and amount:
            if user.fine > 0:
                if user.fine > int(amount):
                    user.fine -= int(amount)
                    user.save()
                elif user.fine == int(amount):
                    user.fine = 0
                    user.save()
                else:
                    messages.error(request, 'Invalid amount')
                    return redirect('repay_due')

                TransactionLog.objects.create(user=user, amount=amount, transaction_type='payment amount: ' + str(amount))
                context = {
                    'name': user.name,
                    'fine': user.fine,
                }
                messages.success(request, 'Fine paid successfully')
                return render(request, 'payment.html', context)
            else:
                messages.error(request, 'You have no fine')
                return redirect('repay_due')
        else:
            messages.error(request, 'Invalid details')
            return redirect('repay_due')
    return render(request, 'payment.html', {})
                

@login_required()
@permission_required('librarian')
def edit_book(request, book_id):
    book = get_object_or_404(Book, access_code=book_id)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book edited successfully')
            return redirect('lib_book')
        else:
            messages.error(request, 'Invalid details')
            print(form.errors)  # Debugging statement
            return redirect('lib_book')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form, 'book_id': book_id})


@login_required()
@permission_required('librarian')
def edit_magazine(request, magazine_id):
    magazine = get_object_or_404(Magazine, id=magazine_id)
    if request.method == "POST":
        form = MagForm(request.POST, instance=magazine)
        if form.is_valid():
            form.save()
            return redirect('lib_mag')
    else:
        form = MagForm(instance=magazine)
    return render(request, 'edit_magazine.html', {'form': form})

"""
@login_required()
@permission_required('librarian')
def edit_reference(request, reference_id):
    reference = get_object_or_404(Reference, id=reference_id)
    if request.method == "POST":
        form = ReferenceForm(request.POST, instance=reference)
        if form.is_valid():
            form.save()
            return redirect('lib_reference')
    else:
        form = MagForm(instance=reference)
    return render(request, 'edit_reference.html', {'form': form})
"""


@login_required()
@permission_required('librarian')
def edit_student(request, id):
    student = get_object_or_404(Users, id_number=id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student edited successfully')
            return redirect('lib_student')
        else:
            messages.error(request, 'Invalid details')
            return redirect('lib_student')
    else:
        form = UserForm(instance=student)
    return render(request, 'edit_student.html', {'form': form})


@login_required()
@permission_required('librarian')
def edit_staff(request, id):
    staff = get_object_or_404(Users, id_number=id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff edited successfully')
            return redirect('lib_staff')
        else:
            messages.error(request, 'Invalid details')
            return redirect('lib_staff')
    else:

        form = UserForm(instance=staff)
    return render(request, 'edit_staff.html', {'form': form})


@login_required()
@group_required('student', 'staff')
def books(request, name=None):
    user = Users.objects.get(username=request.user.username)
    if user.user_type not in [2, 3]:  # 2 and 3 are the user types for staff and student
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login_user')
    if request.method == 'POST':
        query = request.POST.get('query')
        results = Book.objects.filter(Q(name__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query) | Q(access_code__icontains=query))
        lis = []
        for i in results:
            lis.append({
                'name': i.name,
                'isbn': i.isbn,
                'copies': [copy.available_copies for copy in i.copies.all()],
                'edition': i.edition,
                'reference': i.reference,
                'author': i.author,
                'available_on': i.ret_date,
            })
        return render(request, 'book.html', {'list': lis})
    else:
        return render(request, "book.html", {})


@login_required()
@group_required('student', 'staff')
def mag(request):
    user = Users.objects.get(username=request.user.username)
    if user.user_type not in [2, 3]:  # 2 and 3 are the user types for staff and student
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login_user')
    obj = Magazine.objects.all()
    lis = []
    for i in obj:
        lis.append({
            'name': i.name,
            'isbn': i.isbn,
            'author': i.author,
            'category': i.category,
            'edition': i.edition,
        })
    print(lis)
    return render(request, "mag.html", {'list': lis})


@login_required()
@permission_required('librarian')
def add_book(request):
    print(request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        isbn = request.POST.get('isbn')
        author = request.POST.get('author')
        copies = request.POST.get('copies')
        reference = True if request.POST.get('reference') == 'on' else False
        edition = request.POST.get('edition')
        category = request.POST.get('category')
        cost = request.POST.get('price')
        year = request.POST.get('year')
        publisher = request.POST.get('publisher')
        access_code = request.POST.get('code')
        if name and isbn and author and copies and category:
            if Book.objects.filter(access_code=access_code).exists():
                messages.error(request, 'Book already exists')
                return redirect('add_book')
            else:
                for _ in range(int(copies)):
                    access_codes = int(access_code) + int(_)
                    book = Book(name=name, isbn=isbn, author=author, category=category, edition=edition, reference=reference, cost=cost, pub_year=year, publisher=publisher, access_code=access_codes)
                    book.save()
                messages.success(request, 'Book added successfully')
                return redirect('add_book')
        return render(request, 'add_book.html', {})
    else:
        return render(request, 'add_book.html', {})


@login_required()
@permission_required('librarian')
def add_magazine(request):
    print(request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        isbn = request.POST.get('isbn')
        author = request.POST.get('author')
        category = request.POST.get('category')
        edition = request.POST.get('edition')
        if name and isbn and author and edition and category:
            if Magazine.objects.filter(isbn=isbn).exists():
                messages.error(request, 'Magazine already exists')
                return redirect('add_magazine')
            else:
                magazine = Magazine(name=name, isbn=isbn, author=author, category=category, edition=edition)
                magazine.save()
                messages.success(request, 'Magazine added successfully')
                return redirect('add_magazine')
        return render(request, 'add_magazine.html', {})

    return render(request, 'add_magazine.html', {})


@login_required()
@permission_required('librarian')
def add_staff(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        staff_id = request.POST.get('staff_id')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
        else:
            photo = None
        if name and staff_id and email and phone and password:
            if Users.objects.filter(id_number=staff_id).exists():
                messages.error(request, 'Staff already exists')
                return redirect('add_staff')
            else:
                if photo:
                    fs = FileSystemStorage()
                    pic_name = fs.save(photo.name, photo)
                    url = fs.url(pic_name)
                    user = Users.objects.create_user(username=staff_id, id_number=staff_id, email=email, password=password, name=name, phone=phone, user_type=2, photo=url)
                else:
                    user = Users.objects.create_user(username=staff_id, id_number=staff_id, email=email, password=password, name=name, phone=phone, user_type=2, photo=None)

                staff_group, created = Group.objects.get_or_create(name='staff')
                if created:
                    print("staff group created")
                staff_group.user_set.add(user)
                user.save()
                messages.success(request, 'Staff added successfully')
                return redirect('add_staff')
        return render(request, 'add_staff.html', {})
    else:
        return render(request, 'add_staff.html', {})


@login_required()
@permission_required('librarian')
def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        usn = request.POST.get('usn')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
        else:
            photo = None
        if name and usn and email and phone and password:
            if Users.objects.filter(username=usn).exists():
                messages.error(request, 'Student already exists')
                return redirect('add_student')
            else:
                if photo:
                    fs = FileSystemStorage()
                    pic_name = fs.save(photo.name, photo)
                    url = fs.url(pic_name)
                    user = Users.objects.create_user(username=usn, id_number=usn, email=email, password=password, name=name, phone=phone, user_type=3, photo=url)
                else:
                    user = Users.objects.create_user(username=usn, id_number=usn, email=email, password=password, name=name, phone=phone, user_type=3, photo=None)
                student_group, created = Group.objects.get_or_create(name='student')
                if created:
                    print("student group created")
                student_group.user_set.add(user)
                user.save()
                messages.success(request, 'Student added successfully')
                return redirect('add_student')
        return render(request, 'add_student.html', {})
    else:
        return render(request, 'add_student.html', {})


def rules(request, id=None):
    if id:
        t = get_object_or_404(Users, id=id)
        context = {
            'name': t.name,
        }
        return render(request, 'rules.html', context)
    else:
        return render(request, 'rules.html', {})


def secret(request):
    return render(request, 'secret.html', {})


@login_required()
@group_required('librarian')
def searchstu(request, query):
    results = Users.objects.filter(id_number__icontains=query)
    return render(request, 'search.html', {'results': results})


@login_required()
@group_required('librarian')
def searchstaff(request, query):
    results = Users.objects.filter(id_number__icontains=query)
    return render(request, 'lib_student.html', {'results': results})


@login_required()
@group_required('librarian')
def searchbook(request, query):
    results = Book.objects.filter(name__icontains=query)
    return render(request, 'search.html', {'results': results})


@login_required()
@group_required('librarian')
def searchtransac(request, query):
    results = TransactionLog.objects.filter(user__id_number__icontains=query)
    return render(request, 'transaction_logs.html', {'results': results})


@login_required()
@group_required('student', 'staff')
def search(request):
    form = SearchForm(request.POST)
    if form.is_valid():
        query = form.cleaned_data['query']
        print(query)
        obj = Book.objects.filter(name__icontains=query)
        lis = []
        for i in obj:
            lis.append({
                'name': i.name,
                'isbn': i.isbn,
                'copies': i.copies,
                'edition': i.edition,
                'author': i.author,
                'available_on': i.ret_date,
            })
        print(lis)
        return render(request, "search.html", {'list': lis})
    return render(request, 'search.html', {'form': form})

@login_required()
@group_required('student', 'staff')
def contact(request):
    #todo make a contact us form to send directly to admin
    if request.POST:
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        sender = request.user
        new_messsage = Message.objects.create(subject=subject, sender=sender, content=message)
        new_messsage.save()
        return render(request, 'thank_you.html', {})
    return render(request, 'contact_us.html', {})


def home(request):
    return render(request, 'home.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, 'you have successully logged out')
    return redirect('login')

@login_required()
@group_required('staff')
def staff_dashboard(request, id):
    user = Users.objects.get(id_number=id)
    context = {
        'user': user,
    }
    return render(request, 'staff_dash.html', context)

@login_required()
@group_required('student', 'staff')
def files(request):
    obj = File.objects.all()
    lis = []
    for i in obj:
        lis.append({
            'title': i.title,
            'description': i.description,
            'file': i.file,
            'date': i.date_uploaded,
        })
    print(lis)
    return render(request, "files.html", {'list': lis})


@login_required()
@group_required('staff')
def files_delete(request, id):
    try:
        obj = File.objects.filter(user_num=id)
        obj.delete()
    except:
        messages.error(request, 'You do not have permission to delete this file')
        return redirect('files')
    return redirect('files')


@login_required()
@group_required('staff')
def staff_files(request, id):
    if request.method == 'POST':
        file = request.FILES['document']
        title = request.POST.get('title')
        description = request.POST.get('desp')
        print(title, description, file)
        fs = FileSystemStorage()
        name = fs.save(file.name, file)
        url = fs.url(name)
        user = Users.objects.get(id_number=id)
        new_file = File(file=url, title=title, description=description, user=user)
        new_file.save()
        messages.success(request, 'File uploaded successfully')
        return redirect('staff_files', id=id)
    obj = File.objects.filter(user=id)
    user = Users.objects.get(id_number=id)
    lis = []
    for i in obj:
        lis.append({
            'id': user.id_number,
            'from': user.name,
            'title': i.title,
            'description': i.description,
            'file': i.file,
        })
    print(lis)
    return render(request, "staff_files.html", {'list': lis, 'id': id})

@login_required()
@permission_required('librarian')
def lib_files(request):
    if request.method == 'POST':
        file = request.FILES['document']
        title = request.POST.get('title')
        description = request.POST.get('desp')
        print(title, description, file)
        fs = FileSystemStorage()
        name = fs.save(file.name, file)
        url = fs.url(name)
        new_file = File(file=url, title=title, description=description, user=request.user)
        new_file.save()
        messages.success(request, 'File uploaded successfully')
        return redirect('lib_files')
    obj = File.objects.all()
    lis = []
    for i in obj:
        lis.append({
            'id': i.id,
            'title': i.title,
            'description': i.description,
            'file': i.file,
            'from': i.user.name,
            'date': i.date_uploaded,
        })
    print(lis)
    return render(request, "lib_files.html", {'list': lis})


@login_required()
@permission_required('librarian')
def lib_files_delete(request, id):
    obj = File.objects.get(id=id)
    obj.delete()
    return redirect('lib_files')


@login_required()
@permission_required('librarian')
def lib_notif_delete(request, id):
    obj = Notification.objects.get(id=id)
    obj.delete()
    return redirect('lib_notification')


@login_required()
def notification(request):
    obj = Notification.objects.all()
    lis = []
    for i in obj:
        lis.append({
            'title': i.title,
            'content': i.content,
            'date': i.date_uploaded,
        })
    print(lis)
    return render(request, "notification.html", {'list': lis})


@login_required()
@permission_required('librarian')
def lib_notification(request):
    obj = Notification.objects.all()
    lis = []
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            new_notification = Notification(title=title, content=content)
            new_notification.save()
            messages.success(request, 'Notification added successfully')
            return redirect('lib_notification')
        else:
            messages.error(request, 'Invalid details')
            return redirect('lib_notification')
    for i in obj:
        lis.append({
            'id': i.id,
            'title': i.title,
            'from': request.user.username,
            'content': i.content,
            'date': i.date_uploaded,
        })
    print(lis)
    return render(request, "lib_notification.html", {'list': lis})

@login_required()
@permission_required('librarian')
def transaction_logs(request):
    total = TransactionLog.objects.all().count()
    transaction_logs = TransactionLog.objects.all().order_by('-transaction_date')
    if request.method == 'POST':
        query = request.POST.get('query')
        results = TransactionLog.objects.filter(Q(user__id_number__icontains=query) | Q(transaction_type__icontains=query) | Q(transaction_date__icontains=query)| Q(user__name__icontains=query)).order_by('-transaction_date')
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'transaction_logs.html', {'transaction_logs': results, 'page_obj': page_obj, 'total': total})
    else:
        return render(request, 'transaction_logs.html', {'transaction_logs': transaction_logs, 'total': total})

@login_required()
def transaction_report(request, id):
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, 750, "EAST WEST INSTIUTE OF TECHNOLOGY")

    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 700, "LIBRARY TRANSACTION REPORT")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 650, "Transaction Details")

    transaction = TransactionLog.objects.get(id=id)
    y = 600
    if transaction.amount:
        p.drawString(100, y, f"Transaction ID: {transaction.id}")
        p.drawString( 100, y - 50, f"User: {transaction.user.name}, ID: {transaction.user.id_number}")
        p.drawString(100, y - 100, f"Transaction Type: {transaction.transaction_type} Rs")
        p.drawString(100, y - 150, f"Amount: {transaction.amount} Rs")
        p.drawString(100, y - 200, f"Date: {transaction.transaction_date}")
    else:
        p.drawString(100, y, f"Transaction ID: {transaction.id}")
        p.drawString(100, y - 50, f"User: {transaction.user.name}, ID: {transaction.user.id_number}")
        p.drawString(100, y - 100, f"Transaction Type: {transaction.transaction_type}")
        p.drawString(100, y - 150, f"Date: {transaction.transaction_date}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(250, 1000, "Footer: End of Report")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return FileResponse(io.BytesIO(pdf), as_attachment=True, filename='transaction_report.pdf')


@login_required()
def transaction_reports(request):
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)
    transactions = TransactionLog.objects.all().order_by('-transaction_date')
    y = 600
    for transaction in transactions:
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, 750, "EAST WEST INSTIUTE OF TECHNOLOGY")

        p.setFont("Helvetica-Bold", 18)
        p.drawString(100, 700, "LIBRARY TRANSACTION REPORT")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, 650, "Transaction Details")
        if transaction.amount:
            p.drawString(100, y, f"Transaction ID: {transaction.id}")
            p.drawString( 100, y - 50, f"User: {transaction.user.name}, ID: {transaction.user.id_number}")
            p.drawString(100, y - 100, f"Transaction Type: {transaction.transaction_type} Rs")
            p.drawString(100, y - 150, f"Amount: {transaction.amount} Rs")
            p.drawString(100, y - 200, f"Date: {transaction.transaction_date}")
        else:
            p.drawString(100, y, f"Transaction ID: {transaction.id}")
            p.drawString(100, y - 50, f"User: {transaction.user.name}, ID: {transaction.user.id_number}")
            p.drawString(100, y - 100, f"Transaction Type: {transaction.transaction_type}")
            p.drawString(100, y - 150, f"Date: {transaction.transaction_date}")
        p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return FileResponse(io.BytesIO(pdf), as_attachment=True, filename='transaction_report.pdf')


def get_user_details(request, id):
    user = Users.objects.get(id_number=id)
    if request.method == 'GET':
        serializer = UsersSerializer(user)
        return JsonResponse(serializer.data)

@login_required()
@permission_required('librarian')
def delete_book(request, book_id):
    book = get_object_or_404(Book, access_code=book_id)
    book.delete()
    book_duplicate = Book.objects.filter(isbn=book.isbn).first()
    book_copi = Book_Copies.objects.get(book=book_duplicate)
    book_copi.total_copies -= 1
    book_copi.save()
    book_duplicate.save()

    messages.success(request, 'Book deleted successfully')
    return redirect('lib_book')

@login_required
def send_message(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        print(request.user)
        owner = Users.objects.get(id_number=request.user)  # Replace 'owner' with the actual owner's username
        Message.objects.create(sender=request.user, owner=owner, content=content)
        return redirect('send_message')
    return render(request, 'send_message.html')

@login_required()
@permission_required('librarian')
def view_messages(request):
    messages = Message.objects.all().order_by('-timestamp')
    if request.method == 'POST':
        query = request.POST.get('query')
        results = Message.objects.filter(Q(content__icontains=query) | Q(subject__icontains=query))
        return render(request, 'messages.html', {'messages': results})
    return render(request, 'messages.html', {'messages': messages})

@login_required()
@permission_required('librarian')
def message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    message.read = True
    message.save()
    if request.method == 'POST':
        reply = request.POST.get('content')
        sender_email = request.user.email
        receiver_email = message.sender.email
        send_mail(
            'Reply to your message',
            reply,
            sender_email,
            [receiver_email],
            fail_silently=False,
        )
        return redirect('view_messages')
    return render(request, 'message.html', {'message': message})


@login_required()
@permission_required('librarian')
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    message.delete()
    return redirect('view_messages')

#todo- add clubs

@login_required()
@permission_required('student')
def clubs(request):
    return render(request, 'clubs.html', {})

#todo - add blogs in techclub
def techclub(request, user_id):
    _user = get_object_or_404(Users, pk=user_id)
#todo - add events in techclub
#todo - add projects in techclub

def attendance_details(request):
    details = AttendanceHistory.objects.all().order_by('-date')
    lis = []
    for detail in details:
        lis.append({
            'name': detail.user.name,
            'id_number': detail.user.id_number,
            'date': detail.date,
        })

    return render(request, 'attendance.html', {'list': lis})



