import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="container">
      <h1>Urban Tree Observatory</h1>
      <p>Welcome to the Urban Tree Observatory platform. This application is currently under development.</p>
      <div class="features">
        <div class="feature">
          <h2>Tree Mapping</h2>
          <p>View and search urban trees across Ibagué, Colombia</p>
        </div>
        <div class="feature">
          <h2>Citizen Reporting</h2>
          <p>Report tree issues or concerns</p>
        </div>
        <div class="feature">
          <h2>Data Analysis</h2>
          <p>Analyze environmental impact and tree health</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    h1 {
      color: #2c7a41;
      border-bottom: 2px solid #aae0c0;
      padding-bottom: 10px;
    }
    .features {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      margin-top: 40px;
    }
    .feature {
      flex: 1;
      min-width: 250px;
      padding: 20px;
      background-color: #f5f5f5;
      border-radius: 5px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    h2 {
      color: #205833;
      margin-top: 0;
    }
  `]
})
export class AppComponent { }