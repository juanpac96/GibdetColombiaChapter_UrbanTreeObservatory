import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart } from 'chart.js/auto';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bg-white rounded-lg p-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-green-600">Ibagué Urban Forest Dashboard</h1>
        <p class="text-gray-600 mt-1">Overview of urban tree census data and environmental impact in Ibagué</p>
      </div>
      
      <div class="mb-8">
        <h2 class="text-xl font-semibold text-gray-800 mb-3">Overview</h2>
        
        <h3 class="text-lg font-medium text-gray-700 mb-3">Tree Statistics</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="bg-green-50 p-4 rounded-lg shadow border border-green-100">
            <h4 class="text-xs font-medium text-gray-500 uppercase">Total Trees</h4>
            <p class="text-3xl font-bold text-green-600">96,943</p>
            <p class="text-green-600 text-xs mt-1">Urban Tree Census</p>
          </div>
          
          <div class="bg-blue-50 p-4 rounded-lg shadow border border-blue-100">
            <h4 class="text-xs font-medium text-gray-500 uppercase">Species Count</h4>
            <p class="text-3xl font-bold text-blue-600">439</p>
            <p class="text-blue-600 text-xs mt-1">Total species diversity</p>
          </div>
          
          <div class="bg-purple-50 p-4 rounded-lg shadow border border-purple-100">
            <h4 class="text-xs font-medium text-gray-500 uppercase">Average Height</h4>
            <p class="text-3xl font-bold text-purple-600">17.30 m</p>
            <p class="text-purple-600 text-xs mt-1">Tree canopy height</p>
          </div>
          
          <div class="bg-amber-50 p-4 rounded-lg shadow border border-amber-100">
            <h4 class="text-xs font-medium text-gray-500 uppercase">Tree-per-capita</h4>
            <p class="text-3xl font-bold text-amber-600">0.18</p>
            <p class="text-amber-600 text-xs mt-1">Urban tree index</p>
          </div>
        </div>
      
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <!-- Tree Health Distribution -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4">
            <h3 class="text-lg font-medium text-gray-700 mb-3">Tree Health Distribution</h3>
            <div class="flex justify-center">
              <div class="h-64 w-64">
                <canvas id="healthDistributionChart"></canvas>
              </div>
            </div>
            <div class="flex justify-between mt-4 text-center">
              <div class="text-center">
                <span class="block w-4 h-4 mx-auto rounded-full bg-green-500"></span>
                <span class="text-xs font-medium block mt-1">Healthy</span>
                <span class="text-xs text-gray-500">67,890 trees</span>
              </div>
              <div class="text-center">
                <span class="block w-4 h-4 mx-auto rounded-full bg-yellow-500"></span>
                <span class="text-xs font-medium block mt-1">Needs Attention</span>
                <span class="text-xs text-gray-500">19,389 trees</span>
              </div>
              <div class="text-center">
                <span class="block w-4 h-4 mx-auto rounded-full bg-red-500"></span>
                <span class="text-xs font-medium block mt-1">Critical</span>
                <span class="text-xs text-gray-500">5,817 trees</span>
              </div>
              <div class="text-center">
                <span class="block w-4 h-4 mx-auto rounded-full bg-gray-400"></span>
                <span class="text-xs font-medium block mt-1">Unknown</span>
                <span class="text-xs text-gray-500">3,847 trees</span>
              </div>
            </div>
          </div>
          
          <!-- Recent Activity -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4">
            <h3 class="text-lg font-medium text-gray-700 mb-3">Recent Activity</h3>
            <ul class="space-y-3">
              <li *ngFor="let activity of recentActivities" class="flex items-start">
                <span 
                  [ngClass]="{
                    'bg-green-100 text-green-800': activity.type === 'added',
                    'bg-blue-100 text-blue-800': activity.type === 'updated',
                    'bg-amber-100 text-amber-800': activity.type === 'maintenance'
                  }"
                  class="px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full mr-3 mt-0.5"
                >
                  {{activity.type}}
                </span>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{activity.description}}</p>
                  <p class="text-xs text-gray-500">{{activity.time}} by {{activity.user}}</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <!-- Environmental Impact -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4">
            <h3 class="text-lg font-medium text-gray-700 mb-3">Environmental Impact</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="bg-green-50 p-4 rounded-lg border border-green-100">
                <h4 class="text-xs font-medium text-gray-500 uppercase">CO₂ Absorption</h4>
                <p class="text-2xl font-bold text-green-600">646,867.27</p>
                <p class="text-green-600 text-xs mt-1">Tons</p>
              </div>
              
              <div class="bg-blue-50 p-4 rounded-lg border border-blue-100">
                <h4 class="text-xs font-medium text-gray-500 uppercase">Oxygen Production</h4>
                <p class="text-2xl font-bold text-blue-600">1,727,135.62</p>
                <p class="text-blue-600 text-xs mt-1">Tons/year</p>
              </div>
            </div>
          </div>
          
          <!-- Top Species Distribution -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4">
            <h3 class="text-lg font-medium text-gray-700 mb-3">Top Species Distribution</h3>
            <div class="space-y-2">
              <div class="flex flex-col">
                <span class="text-sm">Ceiba pentandra</span>
                <div class="flex items-center mt-1">
                  <div class="h-2 bg-green-500 rounded" style="width: 15%"></div>
                  <span class="ml-2 text-xs">15,000 (15%)</span>
                </div>
              </div>
              <div class="flex flex-col">
                <span class="text-sm">Quercus humboldtii</span>
                <div class="flex items-center mt-1">
                  <div class="h-2 bg-green-500 rounded" style="width: 12%"></div>
                  <span class="ml-2 text-xs">12,000 (12%)</span>
                </div>
              </div>
              <div class="flex flex-col">
                <span class="text-sm">Tabebuia rosea</span>
                <div class="flex items-center mt-1">
                  <div class="h-2 bg-green-500 rounded" style="width: 10%"></div>
                  <span class="ml-2 text-xs">10,000 (10%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Analytics Section -->
      <div>
        <h2 class="text-xl font-semibold text-gray-800 mb-3">Analytics</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <!-- Monthly Growth Trends -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4">
            <div class="flex justify-between mb-3">
              <h3 class="text-lg font-medium text-gray-700">Monthly Growth Trends</h3>
              <button class="text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z" />
                </svg>
              </button>
            </div>
            <div class="h-64">
              <canvas id="growthTrendsChart"></canvas>
            </div>
          </div>
          
          <!-- Geographic Distribution -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4">
            <div class="flex justify-between mb-3">
              <h3 class="text-lg font-medium text-gray-700">Geographic Distribution</h3>
              <button class="text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z" />
                </svg>
              </button>
            </div>
            <div class="h-64">
              <canvas id="geoDistributionChart"></canvas>
            </div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <!-- Temperature Trends -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4">
            <div class="flex justify-between mb-3">
              <h3 class="text-lg font-medium text-gray-700">Temperature Trends</h3>
              <button class="text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z" />
                </svg>
              </button>
            </div>
            <div class="h-64">
              <canvas id="temperatureTrendsChart"></canvas>
            </div>
          </div>
          
          <!-- Functional Groups -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4">
            <div class="flex justify-between mb-3">
              <h3 class="text-lg font-medium text-gray-700">Functional Groups</h3>
              <button class="text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z" />
                </svg>
              </button>
            </div>
            <div class="h-64">
              <canvas id="functionalGroupsChart"></canvas>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Records Section -->
      <div>
        <h2 class="text-xl font-semibold text-gray-800 mb-3">Records</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Recent Tree Records -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4 overflow-x-auto">
            <h3 class="text-lg font-medium text-gray-700 mb-3">Recent Tree Records</h3>
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Species</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Height</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Health</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr *ngFor="let tree of recentTreeRecords">
                  <td class="px-2 py-2 text-sm">{{tree.id}}</td>
                  <td class="px-2 py-2 text-sm">{{tree.species}}</td>
                  <td class="px-2 py-2 text-sm">{{tree.height}}</td>
                  <td class="px-2 py-2">
                    <span 
                      [ngClass]="{
                        'bg-green-100 text-green-800': tree.health === 'Healthy',
                        'bg-yellow-100 text-yellow-800': tree.health === 'Moderate',
                        'bg-red-100 text-red-800': tree.health === 'Poor'
                      }"
                      class="px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full"
                    >
                      {{tree.health}}
                    </span>
                  </td>
                  <td class="px-2 py-2 text-sm">{{tree.location}}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Recent Climate Data -->
          <div class="bg-white rounded-lg shadow border border-gray-200 p-4 overflow-x-auto">
            <h3 class="text-lg font-medium text-gray-700 mb-3">Recent Climate Data</h3>
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Station</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Temperature</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rainfall</th>
                  <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Humidity</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr *ngFor="let record of climateData">
                  <td class="px-2 py-2 text-sm">{{record.station}}</td>
                  <td class="px-2 py-2 text-sm">{{record.date}}</td>
                  <td class="px-2 py-2 text-sm">{{record.temperature}}°C</td>
                  <td class="px-2 py-2 text-sm">{{record.rainfall}}mm</td>
                  <td class="px-2 py-2 text-sm">{{record.humidity}}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
    }
  `]
})
export class DashboardComponent implements OnInit {
  // Recent activity data
  recentActivities = [
    { type: 'added', description: 'New Ceiba pentandra added in Comuna 6', time: '2 hours ago', user: 'Maria Lopez' },
    { type: 'updated', description: 'Updated health assessment for Quercus #IBG-235', time: '5 hours ago', user: 'John Smith' },
    { type: 'maintenance', description: 'Scheduled pruning for Tabebuia cluster in Comuna 2', time: 'Yesterday', user: 'Carlos Rodriguez' },
    { type: 'added', description: 'Added 5 new Ficus benjamina saplings in Comuna 4', time: '2 days ago', user: 'Maria Lopez' }
  ];

  // Health distribution data
  healthDistribution = [
    { label: 'Healthy', count: 67890, percentage: 70 },
    { label: 'Needs Attention', count: 19389, percentage: 20 },
    { label: 'Critical', count: 5817, percentage: 6 },
    { label: 'Unknown', count: 3847, percentage: 4 }
  ];

  // Recent tree records data
  recentTreeRecords = [
    { id: 'T001', species: 'Ceiba pentandra', height: '25.4m', health: 'Healthy', location: 'Bogotá' },
    { id: 'T002', species: 'Quercus humboldtii', height: '18.2m', health: 'Moderate', location: 'Medellín' },
    { id: 'T003', species: 'Tabebuia rosea', height: '12.8m', health: 'Healthy', location: 'Cali' },
    { id: 'T004', species: 'Ficus benjamina', height: '15.6m', health: 'Poor', location: 'Cartagena' },
    { id: 'T005', species: 'Samanea saman', height: '22.1m', health: 'Healthy', location: 'Barranquilla' }
  ];

  // Climate data
  climateData = [
    { station: 'BOG001', date: '2024-03-15', temperature: '18.5', rainfall: '2.3', humidity: '65' },
    { station: 'MED002', date: '2024-03-15', temperature: '22.1', rainfall: '0.0', humidity: '58' },
    { station: 'CAL003', date: '2024-03-15', temperature: '25.8', rainfall: '1.5', humidity: '72' },
    { station: 'BAR004', date: '2024-03-15', temperature: '28.2', rainfall: '0.8', humidity: '75' },
    { station: 'CTG005', date: '2024-03-15', temperature: '29.5', rainfall: '0.0', humidity: '80' }
  ];

  // Top species data
  topSpecies = [
    { name: 'Ceiba pentandra', count: 15000, percentage: 15 },
    { name: 'Quercus humboldtii', count: 12000, percentage: 12 },
    { name: 'Tabebuia rosea', count: 10000, percentage: 10 }
  ];

  // Geographic distribution data
  geographicDistribution = [
    { name: '1', count: 20000, percentage: 20 },
    { name: '2', count: 18000, percentage: 18 },
    { name: '3', count: 16000, percentage: 16 },
    { name: '4', count: 14000, percentage: 14 },
    { name: '5', count: 12000, percentage: 12 }
  ];

  ngOnInit() {
    // Initialize all charts once the view is ready
    setTimeout(() => {
      this.initializeCharts();
    }, 100);
  }

  private initializeCharts() {
    this.createHealthDistributionChart();
    this.createGrowthTrendsChart();
    this.createGeoDistributionChart();
    this.createTemperatureTrendsChart();
    this.createFunctionalGroupsChart();
  }

  private createHealthDistributionChart() {
    const ctx = document.getElementById('healthDistributionChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Healthy', 'Needs Attention', 'Critical', 'Unknown'],
        datasets: [{
          data: [70, 20, 6, 4],
          backgroundColor: [
            '#10b981', // green
            '#f59e0b', // yellow
            '#ef4444', // red
            '#9ca3af'  // gray
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        cutout: '70%',
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            enabled: true
          }
        }
      }
    });
  }

  private createGrowthTrendsChart() {
    const ctx = document.getElementById('growthTrendsChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Growth (cm)',
          data: [5, 7, 10, 14, 12, 8],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#10b981',
          borderWidth: 2
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              display: true,
              color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
              font: {
                size: 10
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 10
              }
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }

  private createGeoDistributionChart() {
    const ctx = document.getElementById('geoDistributionChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Ibagué', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena'],
        datasets: [{
          label: 'Trees',
          data: [20000, 18000, 15000, 12000, 10000],
          backgroundColor: '#60a5fa',
          borderWidth: 0,
          borderRadius: 4
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              display: true,
              color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
              font: {
                size: 10
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 10
              }
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }

  private createTemperatureTrendsChart() {
    const ctx = document.getElementById('temperatureTrendsChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Temperature (°C)',
          data: [7, 9, 12, 14, 10, 7],
          borderColor: '#f97316',
          backgroundColor: 'rgba(249, 115, 22, 0.1)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#f97316',
          borderWidth: 2
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              display: true,
              color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
              font: {
                size: 10
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 10
              }
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }

  private createFunctionalGroupsChart() {
    const ctx = document.getElementById('functionalGroupsChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['Shade', 'Fruit', 'Native', 'Medicinal', 'Ornamental'],
        datasets: [{
          label: 'Tree Functions',
          data: [85, 60, 90, 70, 75],
          backgroundColor: 'rgba(16, 185, 129, 0.2)',
          borderColor: '#10b981',
          borderWidth: 2,
          pointBackgroundColor: '#10b981',
          pointRadius: 3
        }]
      },
      options: {
        scales: {
          r: {
            beginAtZero: true,
            ticks: {
              display: false,
              stepSize: 20
            },
            pointLabels: {
              font: {
                size: 10
              }
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }
}