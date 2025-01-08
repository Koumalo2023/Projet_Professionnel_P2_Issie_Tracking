import { Routes } from '@angular/router';
import { DashboardComponent } from './layourt/dashboard/dashboard.component';
import { AuthComponent } from './layourt/auth/auth.component';
import { HomeComponent } from './layourt/home/home.component';

export const routes: Routes = [
    {
      path: '',
      component: AuthComponent,
      children: [
        {
          path: '',
          loadChildren: () => import('../app/core/routes/authRoute/auth-routing.module').then((m) => m.AuthRoutingModule)
        }
      ]
    },
    {
      path: '',
      component: HomeComponent,
      children: [
        {
          path: '',
          loadChildren: () => import('../app/core/routes/homeRoute/home.module').then((m) => m.HomeModule)
        }
      ]
    },
    {
      path: '',
      component: DashboardComponent,
      children: [
        {
          path: 'dashboard',
          loadComponent: () => import('../app/pages/adminModule/admin-dashboard/admin-dashboard.component').then((m) => m.AdminDashboardComponent)
        },
        {
          path: '',
          loadComponent: () => import('../app/pages/adminModule/admin-dashboard/admin-dashboard.component').then((m) => m.AdminDashboardComponent)
        },
        
        {
          path: '',
          loadChildren: () => import('../app/core/routes/adminRoute/admin-routing.module').then((m) => m.AdminRoutingModule)
        }
      ]
    },
    { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
    { path: '**', redirectTo: '/dashboard' }
  ];