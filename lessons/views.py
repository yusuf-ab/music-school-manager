from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from django import forms
from django.forms.models import model_to_dict
from django.urls import reverse
from functools import wraps

from lessons.forms import SignUpForm, LogInForm, UserForm, BookingForm, UserSelectForm, ChildForm, TransferForm, InvoiceForm, CreateLessonRequestForm, TermForm
from lessons.models import User, Request, Booking, Child, Invoice, Transfer, Term
from datetime import date, datetime, timedelta
from calendar import HTMLCalendar

# Decorator which can be used to limit which user roles can see a page
def allowed_roles(roles):
    def decorator(view_function):
        @login_required
        @wraps(view_function)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.role not in roles:
                return HttpResponse('403 Forbidden')
            else:
                return view_function(request, *args, **kwargs)
        return wrapper
    return decorator

# Create your views here.
def home(request):
    return render(request, 'home.html')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lessons')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

""" Page used for users to login"""
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                
                # Redirect user depending on their role
                if next:
                    return redirect(next)
                elif user.role in [User.DIRECTOR, User.SUPER_ADMIN]:
                    return redirect('permissions')
                elif user.role == User.ADMIN:
                    return redirect('manage_lessons')
                elif user.role == User.STUDENT:
                    return redirect('list_lessons')
                elif user.role == User.TEACHER:
                   return redirect('schedule')
                else:
                    return redirect('home')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next': next})

def log_out(request):
    logout(request)
    return redirect('home')

# Shows the schedule of lessons for a teacher / student as a calander view
@allowed_roles([User.STUDENT, User.TEACHER])
def schedule(request,year,month):

    # Check if date is valid
    try:
        datetime(year,month,1)
    except ValueError:
        return HttpResponse('Invalid Date')
    
    c=HTMLCalendar()

    # Work out the previous month for the previous month button
    if month == 12:
        # If the month is december, the next month is next year
        next_month = reverse('schedule_custom',args=[year+1, 1])
    else:
        next_month = reverse('schedule_custom',args=[year, month+1])

    # Work out the next month for the next month button
    if month == 1:
        # If the month is january, the previous month is december last year
        previous_month = reverse('schedule_custom',args=[year-1, 12])
    else:
        previous_month = reverse('schedule_custom',args=[year, month-1])

    if request.user.role == User.STUDENT:
        # Get all bookings for a student
        bookings =  Booking.objects.filter(client=request.user)
    else:
        # Get all bookings for a teacher
        bookings = Booking.objects.filter(teacher=request.user)

    # Get all the lesson dates for all the bookings
    # as a tuple of the date and booking
    bookingMap = [(t,b) for b in bookings for t in b.dates()]

    # Create a dictionary where the keys are dates
    # and the values are a booking which has lessons on that date
    # The dictionaries keys are sorted by dates ascending
    bookingDateGroup={}
    for x, y in bookingMap:
        bookingDateGroup.setdefault(x, []).append(y)
        bookingDateGroup.setdefault(x, []).sort(key=lambda x: x.time)

    # Generate HTML to display the month for the calander
    monthHTML = c.formatmonthname(year, month, withyear=True)
    # Generate HTML to display the days of the week for the calander
    weekHTML = c.formatweekheader()

    # Generate calander with all the bookings
    cal=''

    # Generate and add each week to the calander at a time
    # by iterating over each week of the month
    for week in c.monthdays2calendar(year, month):
        weeks = ''
        # Iterate over each day of the week
        for d, w in week:
            # If the d=0, then it means that week is in a different month
            # so it should appear as empty
            if d == 0:
                weeks+=f"<td></td>"
            else:
                l = ''
                # Check if there are any lessons on that day
                if date(year,month,d) in bookingDateGroup.keys():

                    # Add a link to each booking with lessons on that day
                    for booking in bookingDateGroup[date(year,month,d)]:
                        # Get the url of the booking
                        url = reverse('view_booking', args=[booking.id])

                        # Display the times of each lesson
                        # eg 1:00pm - 3:00pm
                        start = datetime.combine(date.today(), booking.time)
                        end = start + timedelta(minutes=booking.duration)
                        time_string = start.strftime("%I:%M%p").lower() + ' - ' + end.strftime("%I:%m%p").lower()
                        
                        # Generate the cell for the day
                        l += f'<div><a class="ms-3" href="{url}">{time_string}<a></div>'
                
                # If the date is today, display it bold.
                if date(year,month,d) == date.today():
                    weeks+=f"<td><div class='fw-bold'>{d}</div>{l}</td>"
                else:
                    weeks+=f"<td><div>{d}</div>{l}</td>"
        
        # Add each week as a row to the calander
        cal += f'<tr> {weeks} </tr>\n'

    return render(request,'schedule.html', {'month':monthHTML,'week': weekHTML, 'table': cal,'previous_month':previous_month,'next_month':next_month})

""" Page used by students to request lessons"""
@allowed_roles([User.STUDENT])
def lessons(request):
    if request.method == 'POST':
        form = CreateLessonRequestForm(request.POST, user=request.user)
        form.instance.client = request.user
        if form.is_valid():
            form.save()
            return redirect('list_lessons')
    else:
        form = CreateLessonRequestForm(user=request.user)
    return render(request, "create_lesson_request.html", {"form": form})

# Page for student to view/edit their request
@allowed_roles([User.STUDENT])
def edit_request(request,id):

    if not Request.objects.filter(id=id).exists():
        return HttpResponse('Request not found')

    request_instance=Request.objects.get(id=id)

    if (request_instance.client != request.user):
        return HttpResponse('Unauthorised: Request does not match current user')

    if (request_instance.fulfilled):
        return HttpResponse('Cannot edit a fulfilled request')

    if request.method == 'POST':
        form = CreateLessonRequestForm(request.POST,user=request.user)
        form.instance.id = id
        form.instance.client = request.user
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Request updated successfully")
    else:
        form = CreateLessonRequestForm(user=request.user, instance=request_instance)

    return render(request, "create_lesson_request.html", {"form": form,'edit':True})

""" View used for users to view all their bookings and requests """
@allowed_roles([User.STUDENT])
def list_lessons(request):
    if request.method == 'POST':
        if 'id' in request.POST and request.POST['id'].isnumeric() and Request.objects.filter(id=request.POST['id']).exists():
            delete_request = Request.objects.get(id=request.POST['id'])
            if not delete_request.fulfilled and delete_request.client == request.user:
                delete_request.delete()
    return render(request, 'list_lessons.html',
        {'bookings': Booking.objects.filter(client = request.user),
        'active_requests': Request.objects.filter(client = request.user, fulfilled=False),
        'fulfilled_requests': Request.objects.filter(client = request.user, fulfilled=True)
    })

""" View used for admins to manage all lessons and requests """
@allowed_roles([User.DIRECTOR, User.SUPER_ADMIN, User.ADMIN])
def manage_lessons(request):
    return render(request, 'manage_lessons.html',
        {'bookings': Booking.objects.all(),
        'active_requests': Request.objects.filter(fulfilled=False),
        'fulfilled_requests': Request.objects.filter(fulfilled=True),
        'manage': True
    })

""" A view which displays a booking"""
@allowed_roles([User.STUDENT, User.TEACHER])
def view_booking(request,id):
    booking = Booking.objects.filter(id=id).first()

    # Check that booking exists
    # and make sure students can't view other students bookings for privacy
    if not booking or (request.user.role==User.STUDENT and booking.client != request.user):
        return HttpResponse('Booking does not exist or you don\'t have authorisation to view it')
    return render(request, 'view_booking.html',{'booking':booking})


"""
View used to create or edit lesson bookings
A booking can either be created from scratch
or
be created from an unfulfilled request.

id - the request id or the user id
"""
@allowed_roles([User.DIRECTOR, User.SUPER_ADMIN, User.ADMIN])
def book_lesson(request, id, **kwargs):
    formtype = kwargs.get("type")

    # When a booking is created from scratch,
    # the user has to be selected first
    # this is needed to determine the contents
    # of the child select option field
    # so only children for that user will be displayed
    if formtype == "new":
        form = UserSelectForm()
        if request.method == "POST":
            form = UserSelectForm(request.POST)
            if form.is_valid():
                return redirect('book_lesson_user', id=form.cleaned_data.get('client').id)
        return render(request, 'book_lesson.html', {'form': form})

    # A booking is being edited
    if formtype == "edit":
        if not Booking.objects.filter(id=id).exists():
            return HttpResponse('Booking not found')

        booking = Booking.objects.get(id=id)

        if request.method == "POST":
            form = BookingForm(data=request.POST, instance=booking, user=booking.client)

            if form.is_valid():
                form.save()

                messages.add_message(request, messages.SUCCESS, "Booking updated successfully")

                # Update the invoice, since the number of lessons/duration might have been changed
                invoice = booking.get_invoice
                if invoice is not None:
                    invoice_price = booking.calculate_price()

                    # Price has not changed
                    if invoice.amount == invoice_price:
                        messages.add_message(request, messages.SUCCESS, "Invoice price is the same")

                    # Price has been increased
                    elif invoice.amount < invoice_price:
                        messages.add_message(request, messages.WARNING,
                            f"Pricing for booking has increased by £{invoice_price-invoice.amount:.2f} from £{invoice.amount:.2f} to £{invoice_price:.2f} ")
                        invoice.amount = invoice_price
                        invoice.save()

                    # Price has decreased
                    else:# invoice.amount > invoice_price
                        messages.add_message(request, messages.WARNING,
                            f"Pricing for booking has decreased by £{invoice.amount-invoice_price:.2f} from £{invoice.amount:.2f} to £{invoice_price:.2f} ")

                        invoice.amount=invoice_price
                        invoice.save()

                        invoice.net_paid()
                        refund_amount = invoice.net_paid()-invoice_price

                        messages.add_message(request, messages.WARNING,
                            f"Client currently paid £{invoice.net_paid():.2f} of the invoice")

                        if (refund_amount>0):
                            Transfer.objects.create(
                                invoice =invoice,
                                date = datetime.today(),
                                amount = refund_amount,
                                refund = True
                            )

                            messages.add_message(request, messages.WARNING, f"Client has been given a refund of £{refund_amount:.2f}")
        else:
            form = BookingForm(instance=booking, user=booking.client)
        return render(request, 'book_lesson.html', {'form': form,'edit':True})

    # Check that the request id and user id is valid
    # and retrieve them from the database.
    # Create the booking form.
    if formtype == "req":
        # Booking is being created from an unfulfilled request
        if not Request.objects.filter(id=id).exists():
            return HttpResponse('Request not found')
        elif Request.objects.get(id=id).fulfilled:
            return HttpResponse('Request already fulfilled')

        req = Request.objects.get(id=id)
        client = req.client
        # The booking form is populated with the data from the request
        # to save time for the admin
        form = BookingForm(initial=model_to_dict(req),user=client.id)
    else:
        if not User.objects.filter(id=id).exists():
            return HttpResponse('User not found')
        client = User.objects.get(id=id)
        form = BookingForm(user=client.id)

    # Bookings can only be made for clients
    if client.role != User.STUDENT:
        return HttpResponse('This user is not a student')

    if request.method == 'POST':
        form = BookingForm(request.POST,user=client.id)
        # The client data needs to be added as the client field is excluded in
        # the booking form
        form.instance.client = client
        if form.is_valid():
            # Creates the booking
            thisBooking = form.save()

            # Creates the invoice
            invoice = Invoice(
                booking = thisBooking,
                invoice_ref = thisBooking.invoice_reference(),
                date = datetime.today(),
                due_by_date = thisBooking.date,
                amount = thisBooking.calculate_price(),
                refund = False
            )
            invoice.save()


            if formtype == 'req':
                # Set the request as fulfilled
                req.fulfilled = True
                req.save()
            return redirect('manage_lessons')

    if formtype == "user":
        return render(request, 'book_lesson.html', {'form': form, 'client':  client})
    else:
        return render(request, 'book_lesson.html', {'form': form, 'src_request': req, 'client' : client})


""" Page used by students to record their payments"""
@allowed_roles([User.STUDENT])
def payments(request):
    if request.method == 'POST':
        form = TransferForm(request.POST, user=request.user)

        if form.is_valid():

            # Create the transfer from the form
            get_invoice=form.cleaned_data.get('invoice')
            Transfer.objects.create(
                invoice=get_invoice,
                amount=form.cleaned_data.get('amount'),
                date=form.cleaned_data.get('date'),
                refund=False
            )
            messages.add_message(request, messages.SUCCESS, "Transfer added successfully")

            if (get_invoice.net_paid() < get_invoice.amount):
                # Tell the user how much they have left to pay
                messages.add_message(request, messages.SUCCESS, f"You have £{get_invoice.amount - get_invoice.net_paid():.2f} left to pay on this invoice")
            elif (get_invoice.net_paid() == get_invoice.amount):
                # Tell user they have fully paid
                messages.add_message(request, messages.SUCCESS, "This invoice has now been fully paid")
            else: #(get_invoice.net_paid() >= get_invoice.amount):
                # Tell user they have overpaid

                # Work out how much needs to be refunded and give them a refund
                refund_amount = get_invoice.net_paid() - get_invoice.amount
                Transfer.objects.create(
                    invoice=get_invoice,
                    amount=refund_amount,
                    date=datetime.today(),
                    refund=True
                )
                messages.add_message(request, messages.SUCCESS, f"You have overpaid by £{refund_amount:.2f} and you have been refunded this amount")
    else:
        form = TransferForm(user=request.user)
    return render(request, 'payments.html', {'form': form,'transfers': request.user.transfers(), 'invoices': request.user.invoices()})

""" View for admins to see billing information, such as the balance of each student"""
@allowed_roles([User.DIRECTOR, User.SUPER_ADMIN, User.ADMIN])
def billing(request):
    return render(request, 'billing.html', {'students': User.objects.filter(role=User.STUDENT), 'invoices': Invoice.objects.all(),'transfers': Transfer.objects.all()})
    
@allowed_roles([User.STUDENT,User.ADMIN,User.SUPER_ADMIN,User.DIRECTOR])
def invoice(request, id):
    if not Invoice.objects.filter(id=id).exists():
        return HttpResponse('Invoice not found')

    invoice = Invoice.objects.get(id=id)

    # Don't allow a client to look at another client's invoice
    if request.user.role == User.STUDENT and invoice.booking.client != request.user: 
        return HttpResponse('You cannot view this invoice')
    form = InvoiceForm(instance=invoice)
    return render(request, 'invoice.html', {'form': form})

""" Page for clients to view and add their children """
@allowed_roles([User.STUDENT])
def children(request):
    if request.method == 'POST':
        # New child is being registered
        form = ChildForm(request.POST)
        form.instance.parent = request.user
        if form.is_valid():
            form.save()
            form = ChildForm()
    else:
        form = ChildForm()

    return render(request, 'children.html', {'form': ChildForm(),'child_list': Child.objects.filter(parent=request.user)})

""" Page for super admins to change user permissions """
@allowed_roles([User.DIRECTOR, User.SUPER_ADMIN])
def permissions(request):
    allowed_roles = [User.SUPER_ADMIN, User.ADMIN, User.TEACHER, User.STUDENT]

    if request.method == 'POST':
        user = User.objects.filter(id=request.POST['id']).first()
        if user and request.POST['role'] in allowed_roles:
            user.role = request.POST['role']
            user.save()

    users = User.objects.all()
    return render(request, 'permissions.html', {'users': users, 'choices': User.ROLE_CHOICES, 'allowed_roles' : allowed_roles})

"""Page used to create or edit a user"""
@allowed_roles([User.DIRECTOR, User.SUPER_ADMIN])
def user(request,id):
    if id == 'create':
        title = 'Create new user'
    else:
        title = 'Edit user'

        # Make sure user exists
        if not User.objects.filter(id=id).exists():
            return HttpResponse('User not found')

    if request.method == 'POST':
        if id == 'create':
            form = UserForm(data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('permissions')
        else:
            form = UserForm(data=request.POST, instance=User.objects.get(id=id))
            if form.is_valid():
                form.normal_save()
                return redirect('permissions')
    else:
        if id == 'create':
            form =  UserForm()
        else:
            form = UserForm(instance=User.objects.get(id=id))

    return render(request, 'user.html', {'form': form, 'title': title})

"""Page used to create and view terms"""
@allowed_roles([User.DIRECTOR, User.SUPER_ADMIN, User.ADMIN])
def terms(request):
    form = TermForm()
    if request.method == 'POST':

        if 'delete' in request.POST:
            # A term is being deleted
            Term.objects.filter(id=request.POST['id']).delete()
        else:
            # A term is being created
            form = TermForm(request.POST)
            if form.is_valid():
                form.save()
    return render(request, 'terms.html', {'terms': Term.objects.all().order_by('start_date'), 'form': form})

""" Page used to edit term dates"""
@allowed_roles([User.DIRECTOR, User.SUPER_ADMIN, User.ADMIN])
def edit_term(request,id):

    # Check that term with id exists
    if not Term.objects.filter(id=id).exists():
        return HttpResponse('Term not found')

    form = TermForm(instance=Term.objects.get(id=id))
    if request.method == 'POST':
        form = TermForm(request.POST)
        form.instance.id = id
        if form.is_valid():
            form.save()
            return redirect('terms')

    return render(request, 'edit_term.html', {'form': form})