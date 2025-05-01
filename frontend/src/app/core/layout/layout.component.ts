import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MapComponent } from '../../features/map/map.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-layout',
  templateUrl: './layout.component.html',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet, CommonModule]
})
export class LayoutComponent {
  isSidebarOpen = false;

  toggleSidebar() {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  onActivate(event: any) {
    if (event instanceof MapComponent) {
      event.isSidebarOpen = this.isSidebarOpen;
    }
  }
}
