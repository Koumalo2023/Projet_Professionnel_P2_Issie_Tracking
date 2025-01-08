import { Component} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AlertComponent } from './layourt/sharedComponents/alert/alert.component';
import { LoadingSpinnerComponent } from './layourt/sharedComponents/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, AlertComponent, LoadingSpinnerComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent  {
  title = 'Issue Tracking System';
  
}
