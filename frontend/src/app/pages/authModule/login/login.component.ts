import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { AlertService } from '../../../core/services/alert.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [RouterModule, CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  loginForm: FormGroup;
  loading = false;
  errorMessage = '';
  showPassword: boolean = false;
  showPasswordCriteria: boolean = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private alertService: AlertService
  ) {
    this.loginForm = this.fb.group({
      userName: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    const loginData = this.loginForm.value;

    this.authService.login(loginData).subscribe({
      next: (response) => {
          console.log("Réponse de l'API :", response);
          if (response && response.newToken) {
              this.alertService.showAlert('Connexion réussie !', 'success');
              this.router.navigate(['/home']);
              // this.redirectBasedOnRole(response.userInfo.roles, response.userInfo.appUserId);
          } else {
              this.errorMessage = 'Connexion échouée. Vérifiez vos informations.';
          }
      },
      error: (error) => {
          this.loading = false;
          console.error("Erreur lors de la connexion :", error);
          this.errorMessage = 'Erreur lors de la connexion : ' + (error?.error?.message || 'Erreur inconnue');
      },
      complete: () => {
          this.loading = false;
      }
  });
  
  }

  // Redirection en fonction du rôle de l'utilisateur
  redirectBasedOnRole(roles: string, userId: string) {
    if (roles === 'Admin') {
      this.router.navigate(['/home']);
    } else if (roles === 'Employee' || roles === 'User') {
      this.router.navigate(['/dashboard/user-profile', userId]);
    } else {
      this.errorMessage = 'Rôle utilisateur non reconnu.';
    }
  }
  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }
  // Méthode pour simplifier l'accès aux erreurs de validation dans le HTML
  getErrorMessage(controlName: string, errorName: string): boolean {
    const control = this.loginForm.get(controlName);
    return control?.hasError(errorName) && (control.dirty || control.touched) || false;
  }  
}
