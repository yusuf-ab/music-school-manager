from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import timedelta, date
from django.db.models import Sum
from decimal import Decimal

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    """User Model"""
    username = None # Get rid of default username field
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    # User type
    DIRECTOR = 'DIRECTOR'
    SUPER_ADMIN = 'SUPER_ADMIN'
    ADMIN = 'ADMIN'
    TEACHER = 'TEACHER'
    STUDENT = 'STUDENT'
    ROLE_CHOICES = [
        (DIRECTOR, 'Director'),
        (SUPER_ADMIN, 'Super Admin'),
        (ADMIN, 'Admin'),
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student')
    ]
    #director do what
    #
    #super-admin can create, edit and delete admin accounts
    #
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=STUDENT)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email' # Use email as the username field
    REQUIRED_FIELDS = []

    @property
    def role_name(self):
        return self.get_role_display()

    # Balance Calculations
    def bookings(self):
        return Booking.objects.filter(client=self)
    
    """ Get all users invoices """
    def invoices(self):
        return Invoice.objects.filter(booking__client=self)

    """ Get all users transfers """
    def transfers(self):
        return Transfer.objects.filter(invoice__booking__client=self)

    """ Get the total amount the user has been invoiced """
    def total_invoice_amount(self):
        return self.invoices().aggregate(Sum('amount'))['amount__sum'] or 0

    """ Get the amount the user has paid in total """
    def total_paid(self):
        return Transfer.objects.filter(invoice__booking__client=self, refund=False).aggregate(Sum('amount'))['amount__sum'] or 0
    
    """ Get the amount the user has been refunded in total"""
    def total_refunded(self):
        return Transfer.objects.filter(invoice__booking__client=self, refund=True).aggregate(Sum('amount'))['amount__sum'] or 0

    """ Get the net amount of money the user has paid"""
    def total_paid_net(self):
        return self.total_paid() - self.total_refunded()

    """ Get the amount the user owes """
    def total_owed(self):
        return self.total_invoice_amount() - self.total_paid_net()

# Lesson Models

# Lessons can either every week or every other week
class Interval(models.IntegerChoices):
    WEEK1 = 7, 'Every week'
    WEEk2 = 14, 'Every 2 weeks'

# Possible durations for lessons 
class Duration(models.IntegerChoices):
    MIN30 = 30, '30 minutes'
    MIN45 = 45, '45 minutes'
    MIN60 = 60, '60 minutes'

class Child(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('first_name', 'last_name','parent')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Request(models.Model):
    client =  models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    availability = models.CharField(max_length=1000, blank=False)
    lessons = models.IntegerField(blank=False, validators=[MinValueValidator(1)])
    days_between_lessons = models.IntegerField(blank=False, choices=Interval.choices, default=Interval.WEEK1)
    duration = models.IntegerField(blank=False, choices=Duration.choices, default=Duration.MIN60)
    info = models.CharField(max_length=1000)
    fulfilled = models.BooleanField(blank=False, default=False)

    child = models.ForeignKey(Child, null=True, blank=True, on_delete=models.CASCADE)

    def clean(self):
        # Make sure client is not requesting lessons for another client's child
        if self.child is not None and self.child.parent != self.client:
            raise ValidationError("Child must belong to client")

    """ String that can be used to display the interval between lessons"""
    @property
    def between_name(self):
        return self.get_days_between_lessons_display()

    """ String that can be used to display the duration of each lesson"""
    @property
    def duration_name(self):
        return self.get_duration_display()


class Booking(models.Model):
    client =  models.ForeignKey(User, blank=False, related_name = 'client', on_delete=models.CASCADE, limit_choices_to={'role': User.STUDENT})
    lessons = models.IntegerField(blank=False, validators=[MinValueValidator(1)])
    days_between_lessons = models.IntegerField(blank=False, choices=Interval.choices, default=Interval.WEEK1)
    duration = models.IntegerField(blank=False, choices=Duration.choices, default=Duration.MIN60)
    teacher = models.ForeignKey(User, blank=False, related_name = 'teacher', on_delete=models.CASCADE, limit_choices_to={'role': User.TEACHER})
    date = models.DateField(blank=False) # Start Date
    time = models.TimeField(blank=False)
    child = models.ForeignKey(Child, null=True, blank=True, on_delete=models.CASCADE)

    def clean(self):
        # Make sure the child parent matches the client
        if self.child is not None and self.child.parent != self.client:
            raise ValidationError("Child must belong to client")

    def invoice_reference(self):
        #Invoices have a unique reference number consisting of: [student number] - [invoice number]
        return f"{self.client.id}-{self.id}"

    @property
    def get_invoice(self):
        return Invoice.objects.filter(booking=self).first()

    """ Calculate the price of the lesson in a booking"""
    def calculate_price(self):
        # Each lesson is £30 an hour
        return Decimal(30 * (Decimal(self.lessons) * (Decimal(self.duration)/Decimal(60))))
    
    # Return day of the week, where Monday == 0 ... Sunday == 6
    def day(self):
        return self.date.weekday()

    # Get the dates of of the lessons in the booking
    def dates(self):
        return [self.date + timedelta(self.days_between_lessons*n) for n in range(self.lessons)]

    """ String that can be used to display the interval between lessons"""
    @property
    def between_name(self):
        return self.get_days_between_lessons_display()
    
    """ String that can be used to display the duration of each lesson"""
    @property
    def duration_name(self):
        return self.get_duration_display()

class Invoice(models.Model):
    booking = models.ForeignKey(Booking, blank=False, on_delete=models.DO_NOTHING)
    invoice_ref = models.CharField(max_length=20, blank=False)
    date = models.DateField(blank=False) # Invoice issue date
    due_by_date = models.DateField(blank=False) # Invoice payment deadline
    amount = models.DecimalField(blank=False, max_digits=19, decimal_places=2, validators=[MinValueValidator(1)])
    refund = models.BooleanField(blank=False, default=False)

    """ Check the net amount the user has paid of the invoice"""
    def net_paid(self):
        amount_paid = (Transfer.objects.filter(invoice=self, refund=False).aggregate(Sum('amount'))['amount__sum'] or 0)
        amount_refunded = (Transfer.objects.filter(invoice=self, refund=True).aggregate(Sum('amount'))['amount__sum'] or 0)
        return amount_paid - amount_refunded

    """ Check if the invoice has been fully paid"""
    def paid(self):
        return self.net_paid() >= self.amount

    def __str__(self):
        return str(self.invoice_ref)

class Transfer(models.Model):
    invoice = models.ForeignKey(Invoice, blank=False, on_delete=models.DO_NOTHING)
    date = models.DateField(blank=False) # Payment date
    amount = models.DecimalField(blank=False, max_digits=19, decimal_places=2, validators=[MinValueValidator(1)])
    refund = models.BooleanField(blank=False, default=False)

class Term(models.Model):
    name = models.CharField(max_length=50, blank=False)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    """ Display the start to end date of a term as string"""
    def __str__(self):
        return self.name + ' ' + self.start_date.strftime('%d/%m/%Y') + '-' + self.end_date.strftime('%d/%m/%Y')

    def clean(self):
        if None in [self.name, self.start_date, self.end_date]:
            raise ValidationError(f"Missing data")

        if self.end_date <= self.start_date:
            raise ValidationError(f"End date has to be after the start date")

        overlapping_terms = Term.objects.filter(
            end_date__gte=self.start_date, # If a term exists which ends after this term starts
            start_date__lte=self.end_date # and starts before this term ends, then it overlaps
        )

        # Make sure terms do not overlap
        if overlapping_terms.exists() and not (len(overlapping_terms) == 1 and overlapping_terms[0].id == self.id):
            raise ValidationError(f"This term overlaps with {overlapping_terms[0].name}")

    def current_term():
       return Term.objects.filter(start_date__lte=date.today(), end_date__gte=date.today()).first()

    def next_term():
        return Term.objects.filter(start_date__gt=date.today()).first()
