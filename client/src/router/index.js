import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import DashboardPage from '../views/DashboardPage.vue'
import PortfoliosListPage from '../views/PortfoliosListPage.vue'
import InstrumentsListPage from '../views/InstrumentsListPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import useProfileStore from '../stores/profileStore'
import RegisterPage from '../views/RegisterPage.vue'
import InstrumentPage from '../views/InstrumentPage.vue'
import PortfolioPage from '../views/PortfolioPage.vue'
import InstrumentTypesPage from '../views/InstrumentTypesPage.vue'
import ForbiddenPage from '../views/ForbiddenPage.vue'
import NotFoundPage from '../views/NotFoundPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior: () => ({ top: 0 }),
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
      path: '/portfolios/:id',
      name: 'portfolio',
      component: PortfolioPage,
    },
    {
      path: '/instruments',
      name: 'instruments',
      component: InstrumentsListPage,
    },
    {
      path: '/instruments/:id',
      name: 'instrument',
      component: InstrumentPage,
    },
    {
      path: '/instrument-types',
      name: 'instrument-types',
      component: InstrumentTypesPage,
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
    {
      path: '/forbidden',
      name: 'forbidden',
      component: ForbiddenPage,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundPage,
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
