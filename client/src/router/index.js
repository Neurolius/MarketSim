import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import DashboardPage from '../views/DashboardPage.vue'
import PortfoliosListPage from '../views/PortfoliosListPage.vue'
import InstrumentsListPage from '../views/InstrumentsListPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import useProfileStore from '../stores/profileStore'
import RegisterPage from '../views/RegisterPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginPage,
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardPage,
    },
    {
      path: '/portfolios',
      name: 'portfolios',
      component: PortfoliosListPage,
    },
    {
      path: '/instruments',
      name: 'instruments',
      component: InstrumentsListPage,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfilePage,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage,
    },
  ],
})

const publicPage = ['login', 'register']

router.beforeEach(async (to) => {
  const profileStore = useProfileStore()
  if (!profileStore.isLoaded) {
    await profileStore.fetchMe()
  }
  const isPublic = publicPage.includes(to.name)
  if (!profileStore.isAuthenticated && !isPublic) {
    return { name: 'login' }
  }
  if (profileStore.isAuthenticated && isPublic) {
    return { name: 'dashboard' }
  }
})

export default router
