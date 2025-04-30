import { Routes } from '@angular/router';
import { MapComponent } from './features/map/map.component';
import { AnalyticsComponent } from './features/analytics/analytics.component';
import { TreesComponent } from './features/trees/trees.component';
import { ReportsComponent } from './features/reports/reports.component';
import { AlertsComponent } from './features/alerts/alerts.component';

export const routes: Routes = [
  { path: '', component: MapComponent },
  { path: 'map', component: MapComponent },
  { path: 'trees', component: TreesComponent },
  { path: 'reports', component: ReportsComponent },
  { path: 'alerts', component: AlertsComponent },
  { path: 'analytics', component: AnalyticsComponent },
];
