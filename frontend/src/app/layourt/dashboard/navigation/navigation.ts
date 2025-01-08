export interface NavigationItem {
  title: string;
  route?: string;
  icon: string;
  children?: NavigationItem[];
  isOpen?: boolean;
  roles: string[];
}

export const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    title: 'Dashboard',
    route: '/dashboard',
    icon: 'bi bi-house',
    roles: ['admin', 'employee']
  },
  {
    title: 'Films',
    route: '/manage-movie',
    icon: 'bi bi-film',
    roles: ['admin', 'employee']
  },
  {
    title: 'Séances',
    route: '/manage-showtime',
    icon: 'bi bi-calendar',
    roles: ['admin', 'employee']
  },
  {
    title: 'Cinéma',
    route: '/manage-theater',
    icon: 'bi bi-building',
    roles: ['admin', 'employee']
  },
  {
    title: 'Réservations',
    route: '/manage-reservation',
    icon: 'bi bi-ticket',
    roles: ['admin', 'employee']
  },
  {
    title: 'Employés',
    route: '/manage-employee',
    icon: 'bi bi-people',
    roles: ['admin','employee']
  }
];

