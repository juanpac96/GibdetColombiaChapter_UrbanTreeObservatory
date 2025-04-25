import { Component } from '@angular/core';
import { LayoutComponent } from './core/layout/layout.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  standalone: true,
  imports: [LayoutComponent]
})
export class AppComponent {
  title = 'urban-tree-observatory';
}
