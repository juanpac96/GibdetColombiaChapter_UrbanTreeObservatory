import { Component, AfterViewInit } from '@angular/core';
import * as L from 'leaflet';

@Component({
  selector: 'app-map-page',
  templateUrl: './map-page.component.html',
  styleUrls: ['./map-page.component.css']
})
export class MapPageComponent implements AfterViewInit {

  private map!: L.Map;
  private loadedPoints: Set<string> = new Set();
  private dataLoaded: boolean = false;

  ngAfterViewInit(): void {
    this.initMap();
  }

  private initMap(): void {
    this.map = L.map('map', {
      center: [4.43889, -75.23222],
      zoom: 13,
      zoomControl: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    this.loadGeoJSON();
    this.loadPointsFromMultiplePages(10); // Cargar 10 páginas
  }

  private loadGeoJSON(): void {
    fetch('https://raw.githubusercontent.com/OmdenaAI/GibdetColombiaChapter_UrbanTreeObservatory/main/data/geojson/ibague_communes.geojson')
      .then(response => response.json())
      .then(data => {
        L.geoJSON(data).addTo(this.map);
      })
      .catch(error => console.error('Error al cargar el GeoJSON:', error));
  }

  private async loadPointsFromMultiplePages(pages: number): Promise<void> {
    if (this.dataLoaded) return;
    this.dataLoaded = true;

    const baseUrl = 'http://localhost:8000/api/v1/biodiversity/records/?life_form=TR&limit=100';

    for (let page = 0; page < pages; page++) {
      const offset = page * 100;
      const url = `${baseUrl}&offset=${offset}`;
      try {
        const response = await fetch(url);
        const data = await response.json();

        if (!data.results || !Array.isArray(data.results)) {
          console.warn(`Página ${page + 1}: sin resultados válidos.`);
          continue;
        }

        data.results.forEach((record: any) => {
          const lat = record.latitude;
          const lng = record.longitude;

          if (lat && lng) {
            const key = `${lat.toFixed(5)}_${lng.toFixed(5)}`;
            if (!this.loadedPoints.has(key)) {
              this.loadedPoints.add(key);

              L.circleMarker([lat, lng], {
                radius: 4,
                color: 'black',
                weight: 1,
                fillColor: 'green',
                fillOpacity: 0.5
              })
                .addTo(this.map)
                .bindPopup(`
                  <b>${record.common_name || 'Sin nombre común'}</b><br>
                  <i>${record.species?.scientific_name || 'Sin nombre científico'}</i><br>
                  <b>Sitio:</b> ${record.place?.site || 'Sin sitio'}<br>
                  <b>Fecha:</b> ${record.date || 'Sin fecha'}
                `);
            }
          }
        });

      } catch (error) {
        console.error(`Error al cargar la página ${page + 1}:`, error);
      }
    }
  }
}

