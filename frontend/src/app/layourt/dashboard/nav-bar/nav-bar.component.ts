import { CommonModule } from '@angular/common';
import { Component, EventEmitter, HostListener, OnInit, Output } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [CommonModule, NgbDropdownModule, RouterModule],
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.scss'
})
export class NavBarComponent  {
  @Output() toggleSidebar = new EventEmitter<void>();
 
  isMenuOpen: boolean = false;

  userName: string = "John Doe";
  
  toggleSidebarVisibility() {
    this.toggleSidebar.emit();
  }

 
  toggleUserMenu(event: MouseEvent) {
    event.stopPropagation(); 
    this.isMenuOpen = !this.isMenuOpen;
  }

  @HostListener('document:click', ['$event'])
  closeMenu() {
    this.isMenuOpen = false;
  }

  logout() {
    // Add your logout logic here
    console.log("User logged out");
    // You might want to redirect the user to the login page after logout
  }
}
