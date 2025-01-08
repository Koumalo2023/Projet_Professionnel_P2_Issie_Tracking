import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { NAVIGATION_ITEMS, NavigationItem } from './navigation';

@Component({
  selector: 'app-navigation',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './navigation.component.html',
  styleUrl: './navigation.component.scss'
})
export class NavigationComponent {
  @Input() isSidebarHidden = false;
  userRole: 'admin' | 'employee' = 'employee';
  constructor(private router: Router) {}


  get navigationItems(): NavigationItem[] {
    return NAVIGATION_ITEMS.filter(item => item.roles.includes(this.userRole));
  }

  toggleSubnav(item: NavigationItem): void {
    if (item.children) {
      item.isOpen = !item.isOpen;
    }
  }

  navigateTo(route: string): void {
    this.router.navigate([route]);
  }

}
