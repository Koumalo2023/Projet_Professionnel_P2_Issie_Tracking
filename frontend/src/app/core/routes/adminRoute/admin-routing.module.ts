import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '../../guards/auth.guard';

const routes: Routes = [
  {
    path: '',
    canActivate: [AuthGuard],
    data: { expectedRole: 'Admin, Employee' },
    children: [
      {
        path: 'manage-movie',
        // loadComponent: () => import('../../../pages/adminModule/manage-movie/manage-movie.component').then(m => m.ManageMovieComponent)
      },
      {
        path: 'movie-detail/:id',
        // loadComponent: () => import('../../../pages/adminModule/manage-movie/movie-detail/movie-detail.component').then(m => m.MovieDetailComponent)
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdminRoutingModule { }
