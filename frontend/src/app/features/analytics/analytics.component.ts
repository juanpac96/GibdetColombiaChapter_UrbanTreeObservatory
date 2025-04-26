import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart } from 'chart.js/auto';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-6 space-y-6">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Tree Analytics Dashboard</h1>
        <p class="mt-2 text-gray-600">Comprehensive analysis of urban tree data in Colombia</p>
      </div>

      <!-- Grid Layout -->
      <div class="space-y-4">
        <!-- Circular Charts Row -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Species Distribution</h2>
            <canvas id="speciesChart"></canvas>
          </div>

          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Tree Health Status</h2>
            <canvas id="healthChart"></canvas>
          </div>

          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Family Distribution</h2>
            <canvas id="familyChart"></canvas>
          </div>

          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Functional Groups</h2>
            <canvas id="functionalGroupChart"></canvas>
          </div>
        </div>

        <!-- Line Charts Row -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Monthly Growth Trends</h2>
            <canvas id="growthChart"></canvas>
          </div>

          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Temperature Trends</h2>
            <canvas id="temperatureChart"></canvas>
          </div>

          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Observation Trends</h2>
            <canvas id="observationChart"></canvas>
          </div>

          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Trait Distribution</h2>
            <canvas id="traitChart"></canvas>
          </div>
        </div>

        <!-- Bar Charts Row -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Environmental Impact</h2>
            <canvas id="impactChart"></canvas>
          </div>

          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Geographic Distribution</h2>
            <canvas id="geographicChart"></canvas>
          </div>

          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Measurement Types</h2>
            <canvas id="measurementChart"></canvas>
          </div>

          <div class="bg-white p-4 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Rainfall Patterns</h2>
            <canvas id="rainfallChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Data Tables Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-8">
        <!-- Recent Tree Data Table -->
        <div class="bg-white p-4 rounded-lg shadow">
          <h2 class="text-lg font-semibold mb-4">Recent Tree Records</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Species</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Height</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Health</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr *ngFor="let tree of recentTrees">
                  <td class="px-4 py-2 text-sm">{{ tree.id }}</td>
                  <td class="px-4 py-2 text-sm">{{ tree.species }}</td>
                  <td class="px-4 py-2 text-sm">{{ tree.height }}m</td>
                  <td class="px-4 py-2">
                    <span [class]="getHealthStatusClass(tree.healthStatus)">
                      {{ tree.healthStatus }}
                    </span>
                  </td>
                  <td class="px-4 py-2 text-sm">{{ tree.location }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Recent Climate Data Table -->
        <div class="bg-white p-4 rounded-lg shadow">
          <h2 class="text-lg font-semibold mb-4">Recent Climate Data</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Station</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Temperature</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rainfall</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Humidity</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr *ngFor="let record of climateData">
                  <td class="px-4 py-2 text-sm">{{ record.station }}</td>
                  <td class="px-4 py-2 text-sm">{{ record.date }}</td>
                  <td class="px-4 py-2 text-sm">{{ record.temperature }}°C</td>
                  <td class="px-4 py-2 text-sm">{{ record.rainfall }}mm</td>
                  <td class="px-4 py-2 text-sm">{{ record.humidity }}%</td>
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
export class AnalyticsComponent implements OnInit {
  recentTrees = [
    { id: 'T001', species: 'Ceiba pentandra', height: 25.4, healthStatus: 'Healthy', location: 'Bogotá' },
    { id: 'T002', species: 'Quercus humboldtii', height: 18.2, healthStatus: 'Moderate', location: 'Medellín' },
    { id: 'T003', species: 'Tabebuia rosea', height: 12.8, healthStatus: 'Healthy', location: 'Cali' },
    { id: 'T004', species: 'Ficus benjamina', height: 15.6, healthStatus: 'Poor', location: 'Cartagena' },
    { id: 'T005', species: 'Samanea saman', height: 22.1, healthStatus: 'Healthy', location: 'Barranquilla' }
  ];

  climateData = [
    { station: 'BOG001', date: '2024-03-15', temperature: 18.5, rainfall: 2.3, humidity: 65 },
    { station: 'MED002', date: '2024-03-15', temperature: 22.1, rainfall: 0.0, humidity: 58 },
    { station: 'CAL003', date: '2024-03-15', temperature: 25.8, rainfall: 1.5, humidity: 72 },
    { station: 'BAR004', date: '2024-03-15', temperature: 28.2, rainfall: 0.8, humidity: 75 },
    { station: 'CTG005', date: '2024-03-15', temperature: 29.5, rainfall: 0.0, humidity: 80 }
  ];

  ngOnInit() {
    this.initializeCharts();
  }

  getHealthStatusClass(status: string): string {
    const baseClasses = 'px-2 py-1 text-xs font-medium rounded-full';
    switch (status.toLowerCase()) {
      case 'healthy':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'moderate':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'poor':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  }

  private initializeCharts() {
    this.createSpeciesChart();
    this.createHealthChart();
    this.createGrowthChart();
    this.createImpactChart();
    this.createFamilyChart();
    this.createFunctionalGroupChart();
    this.createGeographicChart();
    this.createTemperatureChart();
    this.createTraitChart();
    this.createMeasurementChart();
    this.createObservationChart();
    this.createRainfallChart();
  }

  private createSpeciesChart() {
    const ctx = document.getElementById('speciesChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Ceiba pentandra', 'Quercus humboldtii', 'Tabebuia rosea', 'Others'],
        datasets: [{
          data: [30, 25, 20, 25],
          backgroundColor: ['#4CAF50', '#8BC34A', '#CDDC39', '#FF9800']
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom', display: false } }
      }
    });
  }

  private createHealthChart() {
    const ctx = document.getElementById('healthChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Healthy', 'Moderate', 'Poor'],
        datasets: [{
          data: [65, 25, 10],
          backgroundColor: ['#4CAF50', '#FFC107', '#F44336']
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom', display: false } }
      }
    });
  }

  private createGrowthChart() {
    const ctx = document.getElementById('growthChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Growth (cm)',
          data: [5, 8, 12, 15, 10, 7],
          borderColor: '#4CAF50',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  private createImpactChart() {
    const ctx = document.getElementById('impactChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['CO₂', 'O₂', 'Shade', 'Water'],
        datasets: [{
          label: 'Impact',
          data: [75, 82, 60, 45],
          backgroundColor: '#2196F3'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    });
  }

  private createFamilyChart() {
    const ctx = document.getElementById('familyChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'polarArea',
      data: {
        labels: ['Fabaceae', 'Moraceae', 'Bignoniaceae', 'Others'],
        datasets: [{
          data: [40, 30, 20, 10],
          backgroundColor: ['#FF9800', '#F44336', '#9C27B0', '#2196F3']
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  }

  private createFunctionalGroupChart() {
    const ctx = document.getElementById('functionalGroupChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['Shade', 'Fruit', 'Native', 'Ornamental', 'Medicinal'],
        datasets: [{
          label: 'Distribution',
          data: [85, 60, 75, 90, 45],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.2)'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  }

  private createGeographicChart() {
    const ctx = document.getElementById('geographicChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena'],
        datasets: [{
          label: 'Trees',
          data: [1200, 800, 600, 400, 300],
          backgroundColor: '#3F51B5'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  private createTemperatureChart() {
    const ctx = document.getElementById('temperatureChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Avg Temp (°C)',
          data: [22, 23, 25, 24, 23, 22],
          borderColor: '#FF5722',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  }

  private createTraitChart() {
    const ctx = document.getElementById('traitChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'bubble',
      data: {
        datasets: [{
          label: 'Traits',
          data: [
            { x: 20, y: 30, r: 15 },
            { x: 40, y: 10, r: 10 },
            { x: 30, y: 20, r: 8 },
            { x: 10, y: 40, r: 12 }
          ],
          backgroundColor: 'rgba(156, 39, 176, 0.6)'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true },
          y: { beginAtZero: true }
        }
      }
    });
  }

  private createMeasurementChart() {
    const ctx = document.getElementById('measurementChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Height', 'DBH', 'Crown', 'Health'],
        datasets: [{
          label: 'Count',
          data: [150, 120, 90, 180],
          backgroundColor: ['#009688', '#00BCD4', '#03A9F4', '#3F51B5']
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  private createObservationChart() {
    const ctx = document.getElementById('observationChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        datasets: [{
          label: 'Observations',
          data: [45, 60, 35, 80],
          borderColor: '#673AB7',
          tension: 0.4,
          fill: true,
          backgroundColor: 'rgba(103, 58, 183, 0.1)'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  }

  private createRainfallChart() {
    const ctx = document.getElementById('rainfallChart') as HTMLCanvasElement;
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Rainfall (mm)',
          data: [120, 90, 150, 180, 60, 30],
          backgroundColor: '#1976D2'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  }
}