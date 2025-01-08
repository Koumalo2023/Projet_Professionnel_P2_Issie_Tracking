import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  isMenuOpen = false;
  isDropdownOpen = false;
  isDropdownMobileOpen = false;
  isSearchOpen = false;
  isLoggedIn = false;
  username = 'John Doe'; 

  searchQuery: string = '';
  
  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }

  onSearch() {
    if (this.searchQuery.trim().length > 0) {
      console.log(`Search query: ${this.searchQuery}`);
      // Handle filtering of sessions and rooms here
      // For example, you could call a service that filters the results
    }
  }


  toggleDropdown() {
    this.isDropdownOpen = !this.isDropdownOpen;
  }

  toggleDropdownMobile() {
    this.isDropdownMobileOpen = !this.isDropdownMobileOpen;
  }

  logout() { 
    console.log('User logged out');
    this.isLoggedIn = false;
  }
}
