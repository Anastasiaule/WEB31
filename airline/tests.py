from django.test import TestCase
# airline/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from model_bakery import baker
from airline.models import Airline, Flight, Passenger, Rate, Ticket

# Тесты для Airline ViewSet
class AirlineViewSetTestCase(APITestCase):
    def setUp(self):
        self.airline = baker.make('Airline')
    
    def test_list_airlines(self):
        url = reverse('airlines-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_airline(self):
        url = reverse('airlines-detail', kwargs={'pk': self.airline.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.airline.name)
    
    def test_create_airline(self):
        url = reverse('airlines-list')
        data = {'name': 'Аэрофлот'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airline.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Аэрофлот')
    
    def test_update_airline(self):
        url = reverse('airlines-detail', kwargs={'pk': self.airline.id})
        data = {'name': 'S7 Airlines'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.airline.refresh_from_db()
        self.assertEqual(self.airline.name, 'S7 Airlines')
    
    def test_delete_airline(self):
        url = reverse('airlines-detail', kwargs={'pk': self.airline.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Airline.objects.count(), 0)

# Тесты для Flight ViewSet
class FlightViewSetTestCase(APITestCase):
    def setUp(self):
        self.airline = baker.make('Airline')
        self.flight = baker.make('Flight', airline=self.airline)
    
    def test_list_flights(self):
        url = reverse('flights-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_flight(self):
        url = reverse('flights-detail', kwargs={'pk': self.flight.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.flight.name)
    
    def test_create_flight(self):
        url = reverse('flights-list')
        data = {
            'name': 'SU-1234',
            'route': 'Москва - Сочи',
            'airline': self.airline.id,
            'price': 5000
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 2)
        self.assertEqual(response.data['name'], 'SU-1234')
    
    def test_update_flight(self):
        url = reverse('flights-detail', kwargs={'pk': self.flight.id})
        data = {
            'name': 'SU-9999',
            'route': self.flight.route,
            'airline': self.airline.id,
            'price': self.flight.price
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.name, 'SU-9999')
    
    def test_delete_flight(self):
        url = reverse('flights-detail', kwargs={'pk': self.flight.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Flight.objects.count(), 0)

# Тесты для Passenger ViewSet
class PassengerViewSetTestCase(APITestCase):
    def setUp(self):
        self.passenger = baker.make('Passenger')
    
    def test_list_passengers(self):
        url = reverse('passengers-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_passenger(self):
        url = reverse('passengers-detail', kwargs={'pk': self.passenger.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], self.passenger.full_name)
    
    def test_create_passenger(self):
        url = reverse('passengers-list')
        data = {
            'full_name': 'Иванов Иван Иванович',
            'passport': '1234567890',
            'phone': '+79991234567'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Passenger.objects.count(), 2)
        self.assertEqual(response.data['full_name'], 'Иванов Иван Иванович')
    
    def test_update_passenger(self):
        url = reverse('passengers-detail', kwargs={'pk': self.passenger.id})
        data = {
            'full_name': 'Петров Петр Петрович',
            'passport': self.passenger.passport,
            'phone': self.passenger.phone
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.passenger.refresh_from_db()
        self.assertEqual(self.passenger.full_name, 'Петров Петр Петрович')
    
    def test_delete_passenger(self):
        url = reverse('passengers-detail', kwargs={'pk': self.passenger.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Passenger.objects.count(), 0)

# Тесты для Rate ViewSet
class RateViewSetTestCase(APITestCase):
    def setUp(self):
        self.rate = baker.make('Rate')
    
    def test_list_rates(self):
        url = reverse('rates-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_rate(self):
        url = reverse('rates-detail', kwargs={'pk': self.rate.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.rate.name)
    
    def test_create_rate(self):
        url = reverse('rates-list')
        data = {
            'name': 'Бизнес',
            'multiplier': 1.5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rate.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Бизнес')
    
    def test_update_rate(self):
        url = reverse('rates-detail', kwargs={'pk': self.rate.id})
        data = {
            'name': 'Первый класс',
            'multiplier': 2.0
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rate.refresh_from_db()
        self.assertEqual(self.rate.name, 'Первый класс')
    
    def test_delete_rate(self):
        url = reverse('rates-detail', kwargs={'pk': self.rate.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Rate.objects.count(), 0)

# Тесты для Ticket ViewSet
class TicketViewSetTestCase(APITestCase):
    def setUp(self):
        self.airline = baker.make('Airline')
        self.flight = baker.make('Flight', airline=self.airline)
        self.passenger = baker.make('Passenger')
        self.rate = baker.make('Rate')
        self.ticket = baker.make('Ticket', flight=self.flight, passenger=self.passenger, rate=self.rate)
    
    def test_list_tickets(self):
        url = reverse('tickets-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_ticket(self):
        url = reverse('tickets-detail', kwargs={'pk': self.ticket.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seat'], self.ticket.seat)
    
    def test_create_ticket(self):
        url = reverse('tickets-list')
        data = {
            'flight': self.flight.id,
            'passenger': self.passenger.id,
            'rate': self.rate.id,
            'seat': '15A'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 2)
        self.assertEqual(response.data['seat'], '15A')
    
    def test_update_ticket(self):
        url = reverse('tickets-detail', kwargs={'pk': self.ticket.id})
        data = {
            'flight': self.flight.id,
            'passenger': self.passenger.id,
            'rate': self.rate.id,
            'seat': '20B'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.seat, '20B')
    
    def test_delete_ticket(self):
        url = reverse('tickets-detail', kwargs={'pk': self.ticket.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ticket.objects.count(), 0)

# Тест для функции ticket_list
class TicketListViewTestCase(APITestCase):
    def setUp(self):
        self.airline = baker.make('Airline')
        self.flight = baker.make('Flight', airline=self.airline)
        self.passenger = baker.make('Passenger')
        self.rate = baker.make('Rate')
        self.ticket = baker.make('Ticket', flight=self.flight, passenger=self.passenger, rate=self.rate)
    
    def test_ticket_list_view(self):
        url = reverse('home')  # Используем имя URL вместо жесткого пути
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Для HTML-ответа проверяем содержимое
        self.assertContains(response, self.ticket.passenger.full_name)







        

class AirlineViewsetTestCase(TestCase):
    def test_list(self):
        self.assertEqual(1, 1)

    def test_get_list(self):
        r = self.client.get('/api/airline/')
        print(r)

    def test_get_list(self):
        airline = Airline.objects.create(
            name="Аэрофлот"
        )
    
        r = self.client.get('/api/airlines/')
        data = r.json()
        print(data)
    
        assert airline.name == data[0]['name']
        assert airline.id == data[0]['id']
        assert len(data) == 1


    def test_create_flight(self):
        airline = baker.make("airline")

        r = self.client.post("/api/flights/", {
            "name": "SU-1234",
            "route": "Москва - Сочи",
            "airline": airline.id,
            "price": 5000
        })
        new_flight_id = r.json()['id']

        flights = Flight.objects.all()
        assert len(flights) == 1

        new_flight = Flight.objects.filter(id=new_flight_id).first()
        assert new_flight.name == 'SU-1234'
        assert new_flight.route == 'Москва - Сочи'
        assert new_flight.airline == airline
        assert new_flight.price == 5000


class FlightViewsetTestCase(TestCase):
    def test_delete_flight(self):
        flights = baker.make("flight", 10)
        r = self.client.get('/api/flights/')
        data = r.json()
        assert len(data) == 10

        flight_id_to_delete = flights[3].id
        self.client.delete(f'/api/flights/{flight_id_to_delete}/')

        r = self.client.get('/api/flights/')
        data = r.json()
        assert len(data) == 9

        assert flight_id_to_delete not in [i['id'] for i in data]

    def test_update_flight(self):
        airline = baker.make("Airline")
        flights = baker.make("Flight", 10, airline=airline)
        flight: Flight = flights[2]

        r = self.client.get(f'/api/flights/{flight.id}/')
        data = r.json()
        assert data['name'] == flight.name

        r = self.client.put(
            f'/api/flights/{flight.id}/', 
            data={
                "name": "SU-9999",
                "route": flight.route,
                "airline": flight.airline.id,
                "price": flight.price
            },
            content_type='application/json'  # Добавляем content-type
        )
        assert r.status_code == 200

        r = self.client.get(f'/api/flights/{flight.id}/')
        data = r.json()
        assert data['name'] == "SU-9999"

        flight.refresh_from_db()
        assert flight.name == "SU-9999"