import { CommonModule } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { Alert, AlertService } from '../../../core/services/alert.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-alert',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alert.component.html',
  styleUrl: './alert.component.scss'
})
export class AlertComponent implements OnInit {
  alert?: Alert;
  private alertSubscription?: Subscription;
  isVisible!: boolean;

  constructor(private alertService: AlertService) {}

  ngOnInit() {
    this.alertSubscription = this.alertService.alert$.subscribe((alert) => {
      this.alert = alert;
      this.isVisible = !!alert.message;
    });
  }

  ngOnDestroy() {
    this.alertSubscription?.unsubscribe();
  }

  dismiss() {
    this.isVisible = false;
  }
}