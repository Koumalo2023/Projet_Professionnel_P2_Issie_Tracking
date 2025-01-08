import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private authService: AuthService, private router: Router) {}
  canActivate(route: ActivatedRouteSnapshot): boolean {
    // Récupérer les rôles autorisés pour cette route
    const expectedRoles = route.data['expectedRole'];
  
    // Obtenir l'utilisateur connecté via AuthService
    const currentUser = this.authService.getCurrentUser();
  
    // Si aucun utilisateur connecté, rediriger vers la page de connexion
    if (!currentUser) {
      this.router.navigate(['/login']);
      return false;
    }
  
    // Vérifier si le rôle de l'utilisateur est dans la liste des rôles attendus
    const userRole = currentUser.roles;
  
    if (expectedRoles.includes(userRole)) {
      return true;
    } else {
      // Si le rôle ne correspond pas, rediriger vers une autre page ou afficher un message
      this.router.navigate(['/unauthorized']);  // Créez une page pour indiquer l'accès non autorisé si nécessaire
      return false;
    }
  }
  
}
