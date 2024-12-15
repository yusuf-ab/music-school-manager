from django.core.validators import RegexValidator
from django import forms
from .models import Transfer, User, Booking, Request, Child, Invoice, Term
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.db.models import Q
from collections import OrderedDict

class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    new_password = forms.CharField(label='Password', widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex='^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='The password must contain an uppercase character, a lowercase character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation password does not match password.')

    def save(self):
        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            password=self.cleaned_data.get('new_password'),
            role=(self.cleaned_data.get('role') or User.STUDENT)
        )
        return user

    # This method is used by the UserForm 
    # When editing an existing user using the form
    # new password is not required
    # keep the password the same if it isn't given
    def normal_save(self):
        self.clean()
        new_password = self.cleaned_data.get('new_password')
        if new_password != '':
            self.instance.set_password(new_password)
        super().save()

class UserForm(SignUpForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','role']

    new_password = forms.CharField(label='Password', widget=forms.PasswordInput(),
        validators=[RegexValidator(regex='^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='The password must contain an uppercase character, a lowercase character and a number'
        )],required=False
    )
    password_confirmation = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput(), required=False)

    def clean(self):
        super().clean()#
        # Password is optional when admin is editing existing user
        # but it is required when creating a new user
        # Make sure password is supplied when creating a new user
        password = self.cleaned_data.get('new_password')
        if self.instance.id is None and (password is None or password == ''):
            self.add_error('new_password', 'Password is required when creating a new user')
            

        
class LogInForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

class UserSelectForm(forms.Form):
    client = forms.ModelChoiceField(queryset=User.objects.filter(role=User.STUDENT),widget=forms.Select)

    def clean(self):
        super().clean()
        if (self.cleaned_data.get('client') == None):
            self.add_error('client', 'Invalid input')

class BookingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        parent=kwargs.pop('user')
        super(BookingForm, self).__init__(*args, **kwargs)

        #Change the order of the fields
        copy=OrderedDict(self.fields)
        for k in ['teacher','child','day_of_week','time','duration','days_between_lessons','term','start_date','end_date']:
            copy.move_to_end(k)
        self.fields=copy

        # Automatically select current term, if it isn't term time, select next term
        self.initial['term'] = (Term.current_term() or Term.next_term())

        # If booking is being edited, set the day of the week and start date to match the current booking
        if self.instance.date:
            self.initial['day_of_week'] = self.instance.date.weekday()
            self.initial['start_date'] = self.instance.date

        self.fields['child'].queryset= Child.objects.filter(parent=parent)

    class Meta:
        model = Booking
        fields = '__all__'
        exclude = ['client','date','lessons']
        widgets = {
            'time': forms.widgets.TimeInput(attrs={'type': 'time'})
        }
        #lambda value: value if value >= datetime.date.today() else raise forms.ValidationError("The date cannot be in the past!")
    
    term = forms.ModelChoiceField(
        queryset=Term.objects.all().order_by('start_date'),
        widget=forms.Select
    )

    day_of_week = forms.ChoiceField(widget=forms.Select, 
        choices=((0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday'))
    )

    start_date = forms.DateField(
        required=False,
        help_text="<br/>(If lessons start mid term, specify the date of the first lesson)",
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    end_date = forms.DateField(
        required=False,
        help_text="<br/>(If end date is not given, lessons will be booked for the entire/rest of the term)",
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    def clean(self):
        super().clean() 
        term = self.cleaned_data.get('term')
        term_start = term.start_date
        term_end = term.end_date

        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        weekday = self.cleaned_data.get('day_of_week')

        # Make sure day of week is the same as the selected start date 
        if start_date and str(start_date.weekday()) != weekday:
            self.add_error('start_date', 'Date does not match selected day of the week')

        # Make sure day of week is the same as the selected end date 
        if end_date and str(end_date.weekday()) != weekday:
            self.add_error('end_date', 'Date does not match selected day of the week')

        # Make sure start date is within selected term
        if start_date and (not(term_start <= start_date <= term_end)):
            self.add_error('start_date', 'Date is not within selected term')

        # Make sure end date is within selected term
        if end_date and (not(term_start <= end_date <= term_end)):
            self.add_error('end_date', 'Date is not within selected term')
        
        if start_date and end_date and (end_date < start_date):
            self.add_error('end_date', 'End date needs to be after start date')

        # Calculate number of lessons

        if start_date:
            first_lesson_date = start_date
        else:
            # Find first date in term that matches weekday selected
            first_lesson_date = term_start
            while str(first_lesson_date.weekday()) != weekday:
                first_lesson_date += timedelta(1)

        days_between_lessons = int(self.cleaned_data.get('days_between_lessons'))

        # Last possible date of lesson
        last_lesson_date = (end_date or term_end)

        lessons = 0

        # Keep iterating to see how many lessons are possible until we reach the last lesson date
        current_lesson = first_lesson_date
        while current_lesson <= last_lesson_date:
            lessons+=1
            current_lesson += timedelta(days_between_lessons)

        if lessons == 0:
            self.add_error('end_date', 'No lessons were able to be booked within these constraints')

        self.instance.date = first_lesson_date
        self.instance.lessons = lessons

class CreateLessonRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        parent=kwargs.pop('user')
        super(CreateLessonRequestForm, self).__init__(*args, **kwargs)
        self.fields['child'].queryset= Child.objects.filter(parent=parent)

    class Meta:
        model = Request
        fields = '__all__'
        exclude = ['client', 'fulfilled']
        widgets = {'info': forms.widgets.Textarea(attrs={'class':'form-control'})}

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['booking', 'invoice_ref', 'date', 'due_by_date', 'amount', 'refund']

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        exclude = ('parent',)

class TransferForm(forms.Form):
    def __init__(self, *args, **kwargs):
        client=kwargs.pop('user')
        super(TransferForm, self).__init__(*args, **kwargs)

        # Only show the client's invoices in the invoice field
        self.fields['invoice'].queryset= Invoice.objects.filter(booking__client=client)
    
    invoice = forms.ModelChoiceField(queryset=Invoice.objects.all())
    amount = forms.DecimalField(decimal_places=2, min_value=0.01)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','max': datetime.today().strftime('%Y-%m-%d')}))

class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = '__all__'
        widgets = {
            'start_date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'end_date': forms.widgets.DateInput(attrs={'type': 'date'})
        }
