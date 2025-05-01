import { Routes } from '@angular/router';
import { MapComponent } from './features/map/map.component';
import { AnalyticsComponent } from './features/analytics/analytics.component';
import { TreesComponent } from './features/trees/trees.component';
import { ReportsComponent } from './features/reports/reports.component';
import { AlertsComponent } from './features/alerts/alerts.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { AboutComponent } from './features/about/about.component';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'map', component: MapComponent },
  { path: 'trees', component: TreesComponent },
  { path: 'reports', component: ReportsComponent },
  { path: 'alerts', component: AlertsComponent },
  { path: 'analytics', component: AnalyticsComponent },
  { path: 'about', component: AboutComponent },
];
