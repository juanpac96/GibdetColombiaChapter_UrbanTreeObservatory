import { Routes } from '@angular/router';
import { MapComponent } from './features/map/map.component';
import { AnalyticsComponent } from './features/analytics/analytics.component';
// import { TreesComponent } from './trees/trees.component';
// import { ReportsComponent } from './reports/reports.component';
// import { AnalysisComponent } from './analysis/analysis.component';

export const routes: Routes = [
  { path: '', component: MapComponent },
  { path: 'map', component: MapComponent },
  { path: 'analytics', component: AnalyticsComponent },
  // { path: 'trees', component: TreesComponent },
  // { path: 'reports', component: ReportsComponent },
  // { path: 'analysis', component: AnalysisComponent },
];
