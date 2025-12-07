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
    help = "Генерируем тестовые данные для авиакомпании"

    def handle(self, *args, **options):
        fake = Faker("ru_RU")

        # Очищаем старые данные
        Ticket.objects.all().delete()
        Passenger.objects.all().delete()
        Flight.objects.all().delete()
        Airline.objects.all().delete()
        Rate.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # 10 юзеров
        users = []
        letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И']
        
        for i in range(10):
            letter = letters[i]
            username = letter * 3 
            password = letter + "123" 
            
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password=password
            )
            users.append(user)
            print(f"Создан пользователь: {username} / {password}")

        # авиакомпании
        airline_names = [
            "Аэрофлот", "S7 Airlines", "Уральские авиалинии", "Победа",
            "Red Wings", "Nordwind Airlines", "Россия", "Utair",
            "Smartavia", "Якутия"
        ]
        
        airlines = []
        for name in airline_names:
            airline = Airline.objects.create(name=name)
            airlines.append(airline)
        
        print(f"Создано {len(airlines)} авиакомпаний")

        # тарифы
        Rate.objects.create(name="Эконом", multiplier=1.0)
        Rate.objects.create(name="Бизнес", multiplier=1.5)
        Rate.objects.create(name="Первый", multiplier=2.0)
        
        rates = Rate.objects.all()
        print(f"Создано {rates.count()} тарифов")

        #рейсы
        flights = []
        for i in range(200):
            airline = random.choice(airlines)
            

            departure = fake.date_time_between(start_date="+1d", end_date="+60d")
            arrival = departure + timedelta(hours=random.randint(1, 8))
            
            flight = Flight.objects.create(
                name=f"SU{i:03d}", 
                route=f"{fake.city()} → {fake.city()}",
                airline=airline,
                price=random.randint(1000, 60000),
                departure_time=departure,
                arrival_time=arrival
            )
            flights.append(flight)
        
        print(f"Создано {len(flights)} рейсов")

        # пассажиры (по 50 на юзера)
        all_passengers = []
        
        # Шрифт для аватарок
        if os.name == "nt":  # Windows
            font_path = "C:/Windows/Fonts/arial.ttf"
        
        for user in users:
            for j in range(50):
                full_name = fake.name()
                
                # аватарку с инициалами
                initials = "".join([x[0] for x in full_name.split()[:2]]).upper()
                
                # Создаем изображение
                img = Image.new('RGB', (128, 128), color='gray')
                draw = ImageDraw.Draw(img)
                
                # круг
                draw.ellipse((0, 0, 128, 128), fill='blue')
                
                #текст
                font = ImageFont.truetype(font_path, 40)
                text_bbox = draw.textbbox((0, 0), initials, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                draw.text(
                    ((128 - text_width) / 2, (128 - text_height) / 2),
                    initials,
                    font=font,
                    fill='white'
                )
                
                # Сохраняем в BytesIO
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                image_file = ContentFile(buffer.getvalue())
                
                # пассажир
                passenger = Passenger.objects.create(
                    full_name=full_name,
                    passport=fake.bothify(text="??######"),
                    phone=fake.phone_number(),
                    user=user
                )
                
                # Сохраняем картинку
                passenger.picture.save(f"{initials}.png", image_file)
                all_passengers.append(passenger)
            
            print(f"Для пользователя {user.username} создано 50 пассажиров")

        #билеты
        for i in range(600):  # 600 билетов
            ticket = Ticket.objects.create(
                flight=random.choice(flights),
                passenger=random.choice(all_passengers),
                rate=random.choice(rates),
                seat=f"{random.randint(1, 30)}{random.choice('ABCDEF')}"
            )
        
        print(f"Создано 600 билетов")
        print("=" * 50)
        print("Готово! Данные успешно созданы.")
        print("=" * 50)
        print("\nПользователи для входа:")
        for i in range(10):
            letter = letters[i]
            print(f"  {letter*3} / {letter}123")