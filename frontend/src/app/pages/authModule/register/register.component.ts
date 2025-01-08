import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { RegisterViewModel } from '../../../core/models/user.models';
import { CommonModule } from '@angular/common';
import { AlertService } from '../../../core/services/alert.service';
import { LoadingService } from '../../../core/services/loading.services';
import { tap } from 'rxjs';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [RouterModule, CommonModule, ReactiveFormsModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss'
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  showPassword: boolean = false;
  showPasswordCriteria: boolean = false;
  isFormValid: boolean = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private alertService: AlertService,
    private loadingService: LoadingService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.registerForm = this.fb.group({
      userName: ['', [Validators.required, Validators.email]],
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      password: ['', [
        Validators.required,
        Validators.minLength(8),
        Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/)
      ]],                                                    // Mot de passe
      confirmPassword: ['', Validators.required],             // Confirmation de mot de passe
      phoneNumber: [''],                                      // Numéro de téléphone (optionnel)
      hiredDate: [''],                                        // Date d'embauche (optionnel)
      position: [''],                                         // Poste (optionnel)
      roles: [[]]                                             // Rôles (optionnel)
    }, { validator: this.passwordMatchValidator });

    // Abonnez-vous aux modifications de l'état de validation du formulaire
    this.registerForm.statusChanges.subscribe(status => {
      this.isFormValid = this.registerForm.valid;
    });
  }

  // Vérifie que le mot de passe et sa confirmation correspondent
  passwordMatchValidator(form: FormGroup) {
    return form.get('password')?.value === form.get('confirmPassword')?.value
      ? null
      : { mismatch: true };
  }

  // Soumet le formulaire d'inscription
  onSubmit(): void {
    if (this.registerForm.valid) {
      this.loadingService.show();
      const registerData = {
        ...this.registerForm.value,
        phoneNumber: this.registerForm.value.phoneNumber || null,
        hiredDate: this.registerForm.value.hiredDate || null,
        position: this.registerForm.value.position || null,
        roles: this.registerForm.value.roles?.length ? this.registerForm.value.roles : null
      };
      this.authService.registerUser(registerData).subscribe(
        () => {
          this.loadingService.hide();
          this.alertService.showAlert('Inscription réussie !', 'success');
          this.router.navigate(['auth/login']);
        },
        (error) => {
          this.loadingService.hide();
          const errorMessage = error?.error?.message || JSON.stringify(error.error);
          this.alertService.showAlert(errorMessage, 'danger');
        }
      );
    }
  }

  // Récupère les messages d'erreur pour les champs de formulaire
  getErrorMessage(controlName: string, errorName: string): boolean {
    const control = this.registerForm.get(controlName);
    return control?.hasError(errorName) && (control.dirty || control.touched) || false;
  }

  // Affiche ou masque le mot de passe
  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }
}
