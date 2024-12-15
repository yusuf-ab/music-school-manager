from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from lessons.models import *
from datetime import date, datetime, timedelta
from faker import Faker
from django.db.utils import IntegrityError
from django.utils import timezone
import random
from decimal import Decimal

# A few lines in this file were 

class Command(BaseCommand):
    def __init__(self):
        self.faker = Faker('en_GB')

    def seed_required_data(self):
        print("Seeding Required Data")
        # ---- EPIC 1
        john = User.objects.create_user('john.doe@example.org',first_name='John',last_name='Doe',password='Password123',role=User.STUDENT)
        User.objects.create_user('petra.pickles@example.org',first_name='Petra',last_name='Pickles',password='Password123',role=User.ADMIN)
        User.objects.create_user('marty.major@example.org',first_name='Marty',last_name='Major',password='Password123',role=User.DIRECTOR)

        User.objects.create_user('ryan.fuller@example.org',first_name='Ryan',last_name='Fuller',password='Password123',role=User.STUDENT)

        # There should be a second administrator account.
        User.objects.create_user('peter.smith@example.org',first_name='Peter',last_name='Smith',password='Password123',role=User.ADMIN)

        # ---- EPIC 2.1: Children

        #User John Doe has two children: Alice Doe and Bob Doe.
        alice = Child.objects.create(first_name='Alice', last_name='Doe', parent=User.objects.get(email='john.doe@example.org'))
        bob = Child.objects.create(first_name='Bob', last_name='Doe', parent=User.objects.get(email='john.doe@example.org'))

        # ---- EPIC 2.2: Terms

        term = Term.objects.create(name='Term one',start_date=date(2022,9,1),end_date=date(2022,10,21))
        Term.objects.create(name='Term two',start_date=date(2022,10,31),end_date=date(2022,12,16))
        Term.objects.create(name='Term three',start_date=date(2023,1,3),end_date=date(2023,2,10))
        Term.objects.create(name='Term four',start_date=date(2023,2,20),end_date=date(2023,3,31))
        Term.objects.create(name='Term five',start_date=date(2023,4,17),end_date=date(2023,5,26))
        Term.objects.create(name='Term six',start_date=date(2023,6,5),end_date=date(2023,7,21))

        # ---- Epic 3.2

        # Seed Teachers
        teacher = User.objects.create_user('norma.noe@example.org',first_name='Norma',last_name='Noe',password='Password123',role=User.TEACHER)
        johns_teacher = User.objects.create_user('jane.doe@example.org',first_name='Jane',last_name='Doe',password='Password123',role=User.TEACHER)

        johns_lesson_request = Request(client=john, availability="any day", lessons=2, days_between_lessons=7, duration=45, info="info", fulfilled=True)
        johns_booking = Booking.objects.create(client =  john,
                    lessons = johns_lesson_request.lessons,
                    days_between_lessons = johns_lesson_request.days_between_lessons,
                    duration = johns_lesson_request.duration,
                    teacher = johns_teacher,
                    date = term.start_date,
                    time = timezone.now() + timedelta(seconds=random.randint(0, 86400)))

        johns_booking_invoice = Invoice.objects.create(
            booking=johns_booking,
            invoice_ref=johns_booking.invoice_reference(),
            date=datetime.today(),
            due_by_date=johns_booking.date,
            amount=johns_booking.calculate_price(),
            refund=False
        )

        Transfer.objects.create(
            invoice=johns_booking_invoice,
            amount=johns_booking.calculate_price(),
            date=datetime.today(),
            refund=False
        )

        alices_lesson_request = Request(client=john, availability="any day", lessons=2, days_between_lessons=7, duration=45, info="info", fulfilled=True, child=alice)
        alices_booking = Booking.objects.create(client =  john,
                    lessons = alices_lesson_request.lessons,
                    days_between_lessons = alices_lesson_request.days_between_lessons,
                    duration = alices_lesson_request.duration,
                    teacher = teacher,
                    date = term.start_date,
                    time = timezone.now() + timedelta(seconds=random.randint(0, 86400)),
                    child=alice)

        alices_booking_invoice = Invoice.objects.create(
            booking=alices_booking,
            invoice_ref=alices_booking.invoice_reference(),
            date=datetime.today(),
            due_by_date=alices_booking.date,
            amount=alices_booking.calculate_price(),
            refund=False
        )

        Transfer.objects.create(
            invoice=alices_booking_invoice,
            amount=alices_booking.calculate_price(),
            date=datetime.today(),
            refund=False
        )

        bobs_lesson_request = Request(client=john, availability="any day", lessons=2, days_between_lessons=7, duration=45, info="info", fulfilled=True, child=bob)
        bobs_booking = Booking.objects.create(client =  john,
                    lessons = bobs_lesson_request.lessons,
                    days_between_lessons = bobs_lesson_request.days_between_lessons,
                    duration = bobs_lesson_request.duration,
                    teacher = teacher,
                    date = term.start_date,
                    time = timezone.now() + timedelta(seconds=random.randint(0, 86400)),
                    child=bob)

        bobs_booking_invoice = Invoice.objects.create(
            booking=bobs_booking,
            invoice_ref=bobs_booking.invoice_reference(),
            date=datetime.today(),
            due_by_date=bobs_booking.date,
            amount=bobs_booking.calculate_price(),
            refund=False
        )

        Transfer.objects.create(
            invoice=bobs_booking_invoice,
            amount=bobs_booking.calculate_price(),
            date=datetime.today(),
            refund=False
        )

    def seed_student(self, s = None):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        if s:
            student = s
        else:
            student = User.objects.create_user(f'{first_name}.{last_name}@example.org'.lower(),first_name=f'{first_name}',last_name=f'{last_name}',password='Password123',role=User.STUDENT)

        day_choices = [i[0] for i in Interval.choices]
        duration_choices=[i[0] for i in Duration.choices]

        # Create request, bookings and children for user

        # Each student is allocated a teacher and all their lessons are given by that teacher.
        teacher = random.choice(User.objects.filter(role="TEACHER"))
        if random.randrange(100) <= 75:
            # Most clients/children have fulfilled lesson requests
            for i in range(1,3):
                child = None

                if random.randint(0,100) <=75:
                    child = Child.objects.create(first_name=self.faker.first_name(),last_name=last_name,parent=student)

                interval = random.choice(day_choices)
                max_lessons=5
                if interval == 14:
                    max_lessons=3

                request = Request.objects.create(
                    client=student,
                    availability="any",
                    lessons=random.randint(1,max_lessons),
                    days_between_lessons=interval,
                    duration=random.choice(duration_choices),
                    info="none",
                    fulfilled=True,
                    child=child)

                term = random.choice(Term.objects.all())

                # Create bookings
                booking = Booking.objects.create(client =  student,
                    lessons = request.lessons,
                    days_between_lessons = request.days_between_lessons,
                    duration = request.duration,
                    teacher = teacher,
                    date = self.faker.date_between(start_date=term.start_date, end_date=term.start_date+timedelta(7)),
                    time = timezone.now() + timedelta(seconds=random.randint(0, 86400)),
                    child = request.child)
                
                invoice = Invoice.objects.create(
                    booking=booking,
                    invoice_ref=booking.invoice_reference(),
                    date=datetime.today(),
                    due_by_date=booking.date,
                    amount=booking.calculate_price(),
                    refund=False
                )
                # Some of the fulfilled requests have been paid, some have been partially paid, a few have overpaid, and some are unpaid. 

                # One in 4 chance no transfer will be paid
                if random.randint(1,4) != 1:

                    Transfer.objects.create(
                        invoice=invoice,
                        amount=random.choice([invoice.amount,invoice.amount*Decimal(1.5),invoice.amount*Decimal(0.5)]),
                        date=datetime.today(),
                        refund=False
                    )
                    
                    # Give refund if overpaid
                    if (invoice.net_paid() >= invoice.amount):

                        refund_amount = invoice.net_paid() - invoice.amount
                        Transfer.objects.create(
                            invoice=invoice,
                            amount=refund_amount,
                            date=datetime.today(),
                            refund=True
                        )

        else:
            # Some students should have unfulfilled lesson requests.
            for i in range(1,3):
                child = None

                if random.randint(0,100) <=75:
                    child = Child.objects.create(first_name=self.faker.first_name(),last_name=last_name,parent=student)

                Request.objects.create(
                    client=student,
                    availability="any",
                    lessons=random.randint(1,5),
                    days_between_lessons=random.choice(day_choices),
                    duration=random.choice(duration_choices),
                    info="none",
                    fulfilled=False,
                    child=child)

    def handle(self, *args, **options):

        # Seed required data
        try:
            self.seed_required_data()
        except IntegrityError:
            print('Required data already seeded')

        # A further 10 teachers also need to be seeded
        teacher = 0
        while teacher <= 10:
            print(f'Seeding Teacher {teacher}',  end='\r')
            try:
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                User.objects.create_user(f'{first_name}.{last_name}@example.org'.lower(),first_name=f'{first_name}',last_name=f'{last_name}',password='Password123',role=User.TEACHER)
                teacher += 1
            except IntegrityError as e:
                print(e)
                continue

        print()

        # Seed 100 students
        user_count = 0
        while user_count <= 100:
            print(f'Seeding Student {user_count}',  end='\r')
            try:
                self.seed_student()
                user_count += 1
            except IntegrityError as e:
                print(e)
                continue
        
        print()
        print('Finished Seeding')
