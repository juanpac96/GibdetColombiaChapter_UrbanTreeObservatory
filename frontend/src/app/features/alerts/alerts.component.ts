import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-alerts',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alerts.component.html',
  styleUrls: ['./alerts.component.scss']
})
export class AlertsComponent {
  alerts = [
    { 
      id: 1, 
      type: 'Disease', 
      severity: 'High', 
      date: '2025-04-18', 
      tree: 'Maple (ID: 2)', 
      description: 'Signs of fungal infection detected on leaves',
      status: 'New'
    },
    { 
      id: 2, 
      type: 'Maintenance', 
      severity: 'Medium', 
      date: '2025-04-16', 
      tree: 'Oak (ID: 1)', 
      description: 'Scheduled pruning required',
      status: 'In Progress'
    },
    { 
      id: 3, 
      type: 'Environmental', 
      severity: 'Low', 
      date: '2025-04-14', 
      tree: 'Pine (ID: 3)', 
      description: 'Soil moisture levels below optimal range',
      status: 'Resolved'
    },
  ];
  
  alertTypes = ['All Types', 'Disease', 'Pest', 'Maintenance', 'Environmental', 'Damage'];
  
  severityLevels = ['All Levels', 'Low', 'Medium', 'High', 'Critical'];
} 