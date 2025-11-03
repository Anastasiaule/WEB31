import os
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker
from datetime import timedelta

from airline.models import Airline, Flight, Passenger, Rate, Ticket


class Command(BaseCommand):
    help = "Generate fake data for Airline app (Airlines, Flights, Passengers, Rates, Tickets)"

    def handle(self, *args, **options):
        fake = Faker("ru_RU")

        # Очистка данных (в порядке зависимостей)
        self.stdout.write("🧹 Очистка старых данных...")
        Ticket.objects.all().delete()
        Passenger.objects.all().delete()
        Flight.objects.all().delete()
        Airline.objects.all().delete()
        Rate.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # === 1. Пользователи ===
        users = []
        for _ in range(30):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="password123"
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS("✅ Создано 30 пользователей"))

        # === 2. Авиакомпании ===
        airline_names = [
            "Аэрофлот", "S7 Airlines", "Уральские авиалинии", "Победа",
            "Red Wings", "Nordwind Airlines", "Россия", "Utair",
            "Smartavia", "Якутия"
        ]

        airlines = []
        for name in airline_names:
            airline = Airline.objects.create(name=name)
            airlines.append(airline)
        self.stdout.write(self.style.SUCCESS(f"✅ Создано {len(airlines)} авиакомпаний"))

        # === 3. Тарифы ===
        rates = [
            Rate.objects.create(name="Эконом", multiplier=1.0),
            Rate.objects.create(name="Бизнес", multiplier=1.5),
            Rate.objects.create(name="Первый", multiplier=2.0)
        ]
        self.stdout.write(self.style.SUCCESS("✅ Созданы тарифы"))

        # === 4. Рейсы ===
        flights = []
        for _ in range(200):
            airline = random.choice(airlines)
            departure = fake.date_time_between(start_date="+1d", end_date="+90d")
            arrival = departure + timedelta(hours=random.randint(1, 12))
            flight = Flight.objects.create(
                name=fake.bothify(text="??###"),
                route=f"{fake.city()} - {fake.city()}",
                airline=airline,
                price=random.randint(1000, 60000),
                departure_time=departure,
                arrival_time=arrival
            )
            flights.append(flight)
        self.stdout.write(self.style.SUCCESS(f"✅ Создано {len(flights)} рейсов"))

        # === 5. Пассажиры (с инициалами на круглых иконках) ===
        passengers = []
        font_path = None
        try:
            # пробуем найти системный шрифт
            font_path = "C:/Windows/Fonts/arial.ttf" if os.name == "nt" else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        except Exception:
            pass

        def create_avatar(initials: str):
            """Создаёт круглую PNG с инициалами"""
            img_size = 128
            img = Image.new("RGB", (img_size, img_size), color=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
            draw = ImageDraw.Draw(img)
            draw.ellipse((0, 0, img_size, img_size), fill=img.getpixel((0, 0)))
            if font_path:
                font = ImageFont.truetype(font_path, 50)
            else:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), initials, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

            draw.text(((img_size - text_w) / 2, (img_size - text_h) / 2), initials, fill="white", font=font)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return ContentFile(buffer.getvalue(), f"{initials}.png")

        for _ in range(500):
            full_name = fake.name()
            initials = "".join([x[0] for x in full_name.split()[:2]]).upper()
            user = random.choice(users)
            passenger = Passenger.objects.create(
                full_name=full_name,
                passport=fake.bothify(text="??######"),
                phone=fake.phone_number(),
                user=user
            )
            passenger.picture.save(f"{initials}.png", create_avatar(initials))
            passengers.append(passenger)
        self.stdout.write(self.style.SUCCESS(f"✅ Создано {len(passengers)} пассажиров"))

        # === 6. Билеты ===
        for _ in range(1000):
            Ticket.objects.create(
                flight=random.choice(flights),
                passenger=random.choice(passengers),
                rate=random.choice(rates),
                seat=f"{random.randint(1, 30)}{random.choice('ABCDEF')}",
                user=random.choice(users)
            )
        self.stdout.write(self.style.SUCCESS("🎟️ Создано 1000 билетов"))

        self.stdout.write(self.style.SUCCESS("🎉 Генерация данных успешно завершена!"))
