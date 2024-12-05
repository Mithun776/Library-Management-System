from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book, Book_Copies


@receiver(post_save, sender=Book)
def update_book_copies(sender, instance, **kwargs):
    # Count the number of copies of the book
    total_count = Book.objects.filter(isbn=instance.isbn).count()
    issued_count = Book.objects.filter(isbn=instance.isbn, status="issued").count()
    available_count = total_count - issued_count


    # Try to get the Book_Copies instance for the book
    try:
        book_copies = Book_Copies.objects.get(book=instance)
    except Book_Copies.DoesNotExist:
        # If it does not exist, create a new one
        print("Creating new Book_Copies object...")
        book_copies = Book_Copies(book=instance, total_copies=1, issued_copies=0, available_copies=1)
        book_copies.save()

    # Update the number of copies
    book_copies_list = Book_Copies.objects.filter(book__isbn=instance.isbn)
    for book_copies in book_copies_list:
        book_copies.total_copies = total_count
        book_copies.issued_copies = issued_count
        book_copies.available_copies = available_count
        if book_copies.available_copies != available_count:
            Book.status = "error! please check"
        if available_count == 0:
            Book.status = "unavailable"
        book_copies.save()