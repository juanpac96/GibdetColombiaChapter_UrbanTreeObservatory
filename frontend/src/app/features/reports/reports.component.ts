import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-primary-600 mb-6">Reports</h1>
      
      <div class="mb-6 flex flex-wrap justify-between items-center gap-4">
        <div class="flex space-x-2">
          <button class="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
            Create New Report
          </button>
          <button class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300">
            Export Reports
          </button>
        </div>
        
        <div class="flex items-center space-x-2">
          <label for="reportType" class="text-sm font-medium text-gray-700">Filter by Type:</label>
          <select 
            id="reportType" 
            class="border rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option *ngFor="let type of reportTypes">{{type}}</option>
          </select>
        </div>

        <div class="relative">
          <input 
            type="text" 
            placeholder="Search reports..." 
            class="border rounded-lg py-2 px-4 pl-10 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute left-3 top-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tree</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr *ngFor="let report of reports">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{report.id}}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{report.type}}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{report.date}}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{report.tree}}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  [ngClass]="{
                    'bg-green-100 text-green-800': report.status === 'Completed',
                    'bg-yellow-100 text-yellow-800': report.status === 'Pending',
                    'bg-blue-100 text-blue-800': report.status === 'In Progress'
                  }"
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                >
                  {{report.status}}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button class="text-primary-600 hover:text-primary-900 mr-3">View</button>
                <button class="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="mt-4 flex justify-between items-center">
        <div class="text-sm text-gray-700">
          Showing <span class="font-medium">1</span> to <span class="font-medium">3</span> of <span class="font-medium">3</span> reports
        </div>
        <div class="flex space-x-2">
          <button class="px-3 py-1 border rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200">Previous</button>
          <button class="px-3 py-1 border rounded-md bg-primary-600 text-white hover:bg-primary-700">Next</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    /* Reports component specific styles can be added here */
  `]
})
export class ReportsComponent {
  reports = [
    { id: 1, type: 'Inspection', date: '2025-04-15', tree: 'Oak (ID: 1)', status: 'Completed' },
    { id: 2, type: 'Maintenance', date: '2025-04-10', tree: 'Maple (ID: 2)', status: 'Pending' },
    { id: 3, type: 'Health Assessment', date: '2025-04-05', tree: 'Pine (ID: 3)', status: 'Completed' },
  ];
  
  reportTypes = ['All Types', 'Inspection', 'Maintenance', 'Health Assessment', 'Growth Measurement'];
} 