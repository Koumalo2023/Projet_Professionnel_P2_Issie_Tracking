import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export interface Alert {
  message: string;
  type: 'success' | 'danger' | 'warning' | 'info';
  dismissible: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AlertService {
  private alertSubject = new Subject<Alert>();
  alert$ = this.alertSubject.asObservable();

  showAlert(message: string, type: 'success' | 'danger' | 'warning' | 'info', dismissible: boolean = true) {
    this.alertSubject.next({ message, type, dismissible });
    // Délai de 8 secondes pour masquer l'alerte
    setTimeout(() => this.clearAlert(), 5000);
  }

  clearAlert() {
    this.alertSubject.next({ message: '', type: 'info', dismissible: false });
  }
}
