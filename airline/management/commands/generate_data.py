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

        # Очистка данных
        self.stdout.write("🧹 Очистка старых данных...")
        Ticket.objects.all().delete()
        Passenger.objects.all().delete()
        Flight.objects.all().delete()
        Airline.objects.all().delete()
        Rate.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # === 1. Пользователи ===
        users = []
        for i in range(100):
            full_name = fake.name()

            parts = full_name.lower().split()
            username = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else parts[0]

            # Уникальность логина
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Пароль
            if len(parts) >= 2:
                password = f"{parts[0][0]}{parts[1][0]}123"
            else:
                password = f"{parts[0][0]}123"

            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password=password
            )
            users.append(user)

            if (i + 1) % 10 == 0:
                self.stdout.write(f"👤 Создан {i+1}/100: {full_name} | {username} | {password}")

        self.stdout.write(self.style.SUCCESS("✅ Создано 100 пользователей"))

        # === 2. Авиакомпании ===
        airline_names = [
            "Аэрофлот", "S7 Airlines", "Уральские авиалинии", "Победа",
            "Red Wings", "Nordwind Airlines", "Россия", "Utair",
            "Smartavia", "Якутия"
        ]

        airlines = [
            Airline.objects.create(name=name)
            for name in airline_names
        ]

        self.stdout.write(self.style.SUCCESS("✈ Созданы авиакомпании"))

        # === 3. Тарифы ===
        rates = [
            Rate.objects.create(name="Эконом", multiplier=1.0),
            Rate.objects.create(name="Бизнес", multiplier=1.5),
            Rate.objects.create(name="Первый", multiplier=2.0)
        ]
        self.stdout.write(self.style.SUCCESS("💳 Созданы тарифы"))

        # === 4. Рейсы ===
        flights = []
        for _ in range(200):
            airline = random.choice(airlines)

            departure = fake.date_time_between(start_date="+1d", end_date="+60d")
            arrival = departure + timedelta(hours=random.randint(1, 8))

            flight = Flight.objects.create(
                name=fake.bothify(text="??###"),
                route=f"{fake.city()} → {fake.city()}",
                airline=airline,
                price=random.randint(1000, 60000),
                departure_time=departure,
                arrival_time=arrival
            )
            flights.append(flight)

        self.stdout.write(self.style.SUCCESS("🛫 Создано 200 рейсов"))

        # === 5. Пассажиры: 3–5 на каждого пользователя ===
        font_path = (
            "C:/Windows/Fonts/arial.ttf"
            if os.name == "nt"
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        )

        def create_avatar(initials: str):
            img_size = 128
            img = Image.new(
                "RGB",
                (img_size, img_size),
                color=(
                    random.randint(50, 200),
                    random.randint(50, 200),
                    random.randint(50, 200),
                ),
            )
            draw = ImageDraw.Draw(img)
            draw.ellipse((0, 0, img_size, img_size), fill=img.getpixel((0, 0)))
            font = ImageFont.truetype(font_path, 50)
            bbox = draw.textbbox((0, 0), initials, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                ((img_size - text_w) / 2, (img_size - text_h) / 2),
                initials,
                fill="white",
                font=font,
            )

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return ContentFile(buffer.getvalue(), f"{initials}.png")

        all_passengers = []

        for user in users:
            passenger_count = random.randint(3, 5)

            for _ in range(passenger_count):
                full_name = fake.name()
                initials = "".join([x[0] for x in full_name.split()[:2]]).upper()

                passenger = Passenger.objects.create(
                    full_name=full_name,
                    passport=fake.bothify(text="??######"),
                    phone=fake.phone_number(),
                    user=user
                )
                passenger.picture.save(f"{initials}.png", create_avatar(initials))
                all_passengers.append(passenger)

        self.stdout.write(self.style.SUCCESS(f"🧍 Создано {len(all_passengers)} пассажиров"))

        # === 6. Билеты ===
        for i in range(600):
            Ticket.objects.create(
                flight=random.choice(flights),
                passenger=random.choice(all_passengers),
                rate=random.choice(rates),
                seat=f"{random.randint(1, 30)}{random.choice('ABCDEF')}",
            )

        self.stdout.write(self.style.SUCCESS("🎟️ Создано 600 билетов"))
        self.stdout.write(self.style.SUCCESS("🎉 Генерация завершена!"))
