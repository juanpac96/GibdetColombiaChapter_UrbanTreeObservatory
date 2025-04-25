import { Routes } from '@angular/router';
import { MapComponent } from './features/map/map.component';
import { AnalyticsComponent } from './features/analytics/analytics.component';

export const routes: Routes = [
  { path: '', component: MapComponent },
  { path: 'map', component: MapComponent },
  { path: 'analytics', component: AnalyticsComponent },
];
