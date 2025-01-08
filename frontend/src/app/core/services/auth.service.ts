import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable, tap, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { GeneralServiceResponse, LoginResponseViewModel, LoginViewModel, RegisterViewModel, ResetPasswordViewModel, UpdateRoleByIdViewModel, UpdateUserViewModel, User, UserChangePasswordViewModel } from '../models/user.models';


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = `${environment.apiUrl}/Auth`;


  constructor(private http: HttpClient) { }



  //  Inscription d'un nouvel utilisateur
  registerUser(registerViewModel: RegisterViewModel): Observable<GeneralServiceResponse> {
    return this.http.post<GeneralServiceResponse>(
      `${this.apiUrl}/users/register`,
      registerViewModel
    );
  }


  //  Connexion de l'utilisateur
  login(loginViewModel: LoginViewModel): Observable<LoginResponseViewModel | null> {
    return this.http.post<LoginResponseViewModel | null>(`${this.apiUrl}/login`, loginViewModel).pipe(
        tap(response => {
            if (response && response.newToken) { 
                this.storeUserData(response.userInfo, response.newToken);
            }
        })
    );
}

  // Récupère la liste des utilisateurs
    
  getUsersList(): Observable<User[]> {
    return this.http.get<User[]>(
      `${this.apiUrl}/users`);
  }
  //  Détails d'un utilisateur spécifique via son nom
  getUserDetailsByUserName(userName: string): Observable<User | null> {
    return this.http.get<User | null>(
      `${this.apiUrl}/user/${userName}`
    );
  }

  //  Détails d'un utilisateur via son identifiant
  getEmployeeById(userId: string): Observable<User | null> {
    return this.http.get<User | null>(
      `${this.apiUrl}/get-user/${userId}`
    );
  }


  //  Mise à jour d'un utilisateur
  updateUser(updateUserViewModel: UpdateUserViewModel): Observable<GeneralServiceResponse> {
    return this.http.put<GeneralServiceResponse>(
      `${this.apiUrl}/users/update-user`,
      updateUserViewModel
    );
  }


  //  Suppression d'un utilisateur par ID
  deleteUser(userId: string): Observable<GeneralServiceResponse> {
    return this.http.delete<GeneralServiceResponse>(
      `${this.apiUrl}/delete-user/${userId}`
    );
  }

  //  Réinitialisation du mot de passe
  resetEmployeePassword(model: ResetPasswordViewModel): Observable<GeneralServiceResponse> {
    return this.http.post<GeneralServiceResponse>(
      `${this.apiUrl}/reset-password`,
      model
    );
  }

  //  Modification du rôle d'un utilisateur
  changeEmployeeRole(model: UpdateRoleByIdViewModel): Observable<GeneralServiceResponse> {
    return this.http.post<GeneralServiceResponse>(
      `${this.apiUrl}/change-role`,
      model
    );
  }

  
  //  Changement de mot de passe de l'utilisateur
  changePassword(changePasswordViewModel: UserChangePasswordViewModel): Observable<GeneralServiceResponse> {
    return this.http.post<GeneralServiceResponse>(
      `${this.apiUrl}/users/change-password`,
      changePasswordViewModel
    );
  }

  // Fonction pour obtenir l'utilisateur connecté
  getCurrentUser(): User | null {
    if (typeof window !== 'undefined' && localStorage) {
      const userJson = localStorage.getItem('user');
      return userJson ? JSON.parse(userJson) : null;
    }
    return null;
  }

  // Fonction pour sauvegarder l'utilisateur et le token dans le localStorage
  private storeUserData(user: User, token: string): void {
    if (typeof window !== 'undefined' && localStorage) {
      console.log("Utilisateur connecté :", token);
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
    }
  }

  getToken(): string | null {
    if (typeof window !== 'undefined' && localStorage) {
      return localStorage.getItem('token');
    }
    return null;
  }

  // Fonction pour se déconnecter
  logout(): void {
    if (typeof window !== 'undefined' && localStorage) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('authToken');
    }
  }

  // Fonction pour vérifier si un utilisateur est connecté
  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  // Vérifier si l'utilisateur est un administrateur
isAdmin(): boolean {
  const user = this.getCurrentUser();
  return user ? user.roles.includes('Admin') : false;
}

// Vérifier si l'utilisateur est un employé
isEmployee(): boolean {
  const user = this.getCurrentUser();
  return user ? user.roles.includes('Employee') : false;
}

// Vérifier si l'utilisateur est un utilisateur
isUser(): boolean {
  const user = this.getCurrentUser();
  return user ? user.roles.includes('User') : false;
}

}

