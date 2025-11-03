import { createRouter, createWebHistory } from 'vue-router'
import AirlinesView from '@/views/AirlinesView.vue'
import FlightsView from '@/views/FlightsView.vue'
import PassengersView from '@/views/PassengersView.vue'
import RatesView from '@/views/RatesView.vue'
import TicketsView from '@/views/TicketsView.vue'

const routes = [
  {
    path: '/airlines',
    name: 'Airlines',
    component: AirlinesView
  },
  {
    path: '/flights',
    name: 'Flights',
    component: FlightsView
  },
  {
    path: '/passengers',
    name: 'Passengers',
    component: PassengersView
  },
  {
    path: '/rates',
    name: 'Rates',
    component: RatesView
  },
  {
    path: '/tickets',
    name: 'Tickets',
    component: TicketsView
  },
  {
    path: '/',
    redirect: '/airlines'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router