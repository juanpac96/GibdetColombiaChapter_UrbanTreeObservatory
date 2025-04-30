import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-primary-600 mb-6">Dashboard</h1>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <!-- Summary Cards -->
        <div class="bg-green-50 p-4 rounded-lg shadow border border-green-100">
          <h3 class="text-sm font-medium text-green-800">Total Trees</h3>
          <p class="text-3xl font-bold text-green-900">156</p>
          <p class="text-green-700 text-sm mt-1">+12 from last month</p>
        </div>
        
        <div class="bg-blue-50 p-4 rounded-lg shadow border border-blue-100">
          <h3 class="text-sm font-medium text-blue-800">Health Index</h3>
          <p class="text-3xl font-bold text-blue-900">87%</p>
          <p class="text-blue-700 text-sm mt-1">+2% improvement</p>
        </div>
        
        <div class="bg-purple-50 p-4 rounded-lg shadow border border-purple-100">
          <h3 class="text-sm font-medium text-purple-800">Species Diversity</h3>
          <p class="text-3xl font-bold text-purple-900">24</p>
          <p class="text-purple-700 text-sm mt-1">3 new species added</p>
        </div>
        
        <div class="bg-amber-50 p-4 rounded-lg shadow border border-amber-100">
          <h3 class="text-sm font-medium text-amber-800">Maintenance Tasks</h3>
          <p class="text-3xl font-bold text-amber-900">8</p>
          <p class="text-amber-700 text-sm mt-1">3 pending, 5 completed</p>
        </div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Recent Activity -->
        <div class="border rounded-lg shadow p-4">
          <h2 class="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h2>
          <ul class="divide-y divide-gray-200">
            <li *ngFor="let activity of recentActivities" class="py-3 flex items-start">
              <span 
                [ngClass]="{
                  'bg-green-100 text-green-800': activity.type === 'added',
                  'bg-blue-100 text-blue-800': activity.type === 'updated',
                  'bg-amber-100 text-amber-800': activity.type === 'maintenance'
                }"
                class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full mr-3 mt-1"
              >
                {{activity.type}}
              </span>
              <div>
                <p class="text-sm font-medium text-gray-900">{{activity.description}}</p>
                <p class="text-xs text-gray-500">{{activity.time}} by {{activity.user}}</p>
              </div>
            </li>
          </ul>
          <div class="mt-4 text-right">
            <a href="#" class="text-sm font-medium text-primary-600 hover:text-primary-800">
              View all activity →
            </a>
          </div>
        </div>
        
        <!-- Health Distribution -->
        <div class="border rounded-lg shadow p-4">
          <h2 class="text-lg font-semibold text-gray-800 mb-4">Tree Health Distribution</h2>
          <div class="h-64 flex items-end justify-around">
            <div *ngFor="let status of healthDistribution" class="relative w-1/4 mx-1">
              <div 
                [ngStyle]="{'height': status.percentage + '%'}" 
                [ngClass]="{
                  'bg-green-500': status.label === 'Healthy',
                  'bg-yellow-500': status.label === 'Needs Attention',
                  'bg-red-500': status.label === 'Critical',
                  'bg-gray-500': status.label === 'Unknown'
                }"
                class="w-full rounded-t-sm"
              ></div>
              <div class="text-xs text-center mt-2 font-medium">{{status.label}}</div>
              <div class="text-xs text-center text-gray-500">{{status.count}} trees</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="border rounded-lg shadow p-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Recent Tree Updates</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Species</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Health Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Updated</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr *ngFor="let tree of recentTreeUpdates">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{tree.id}}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{tree.species}}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{tree.location}}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    [ngClass]="{
                      'bg-green-100 text-green-800': tree.healthStatus === 'Healthy',
                      'bg-yellow-100 text-yellow-800': tree.healthStatus === 'Needs Attention',
                      'bg-red-100 text-red-800': tree.healthStatus === 'Critical'
                    }"
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  >
                    {{tree.healthStatus}}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{tree.lastUpdated}}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    /* Dashboard component specific styles can be added here */
  `]
})
export class DashboardComponent {
  recentActivities = [
    { type: 'added', description: 'New oak tree added to the database', time: '2 hours ago', user: 'Maria Lopez' },
    { type: 'updated', description: 'Updated health assessment for Maple #42', time: '5 hours ago', user: 'John Smith' },
    { type: 'maintenance', description: 'Scheduled pruning for Pine grove', time: 'Yesterday', user: 'Carlos Rodriguez' },
    { type: 'added', description: 'Added 5 new saplings to inventory', time: '2 days ago', user: 'Maria Lopez' }
  ];

  healthDistribution = [
    { label: 'Healthy', count: 96, percentage: 70 },
    { label: 'Needs Attention', count: 42, percentage: 30 },
    { label: 'Critical', count: 12, percentage: 10 },
    { label: 'Unknown', count: 6, percentage: 5 }
  ];

  recentTreeUpdates = [
    { id: 'T-1234', species: 'Oak', location: 'North Park', healthStatus: 'Healthy', lastUpdated: '2025-04-20' },
    { id: 'T-1235', species: 'Maple', location: 'City Center', healthStatus: 'Needs Attention', lastUpdated: '2025-04-19' },
    { id: 'T-1236', species: 'Pine', location: 'West Gardens', healthStatus: 'Healthy', lastUpdated: '2025-04-18' },
    { id: 'T-1237', species: 'Birch', location: 'River Walk', healthStatus: 'Critical', lastUpdated: '2025-04-17' },
  ];
} 