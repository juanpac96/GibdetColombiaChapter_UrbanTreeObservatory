import { Component, AfterViewInit } from '@angular/core';
import * as L from 'leaflet';
import 'leaflet.markercluster';

@Component({
  selector: 'app-map-page',
  templateUrl: './map-page.component.html',
  styleUrls: ['./map-page.component.css']
})
export class MapPageComponent implements AfterViewInit {

  private map!: L.Map;
  private markerClusterGroup!: L.MarkerClusterGroup;
  private loadedPoints: Set<string> = new Set();
  private dataLoaded: boolean = false;

  // Variables para las capas
  private communeLayer: L.GeoJSON | null = null;

  ngAfterViewInit(): void {
    this.initMap();
  }

  private initMap(): void {
    this.map = L.map('map', {
      center: [4.43889, -75.23222],
      zoom: 13,
      zoomControl: true
    });

    // Cargar la capa base de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    // Crear el grupo de clusters de los puntos
    this.markerClusterGroup = L.markerClusterGroup();
    this.map.addLayer(this.markerClusterGroup);

    // Cargar las capas de comunas y los puntos
    this.loadGeoJSON();
    this.loadAllPoints();
  }

  private loadGeoJSON(): void {
    // Cargar las comunas desde el repositorio en GitHub
    fetch('https://raw.githubusercontent.com/OmdenaAI/GibdetColombiaChapter_UrbanTreeObservatory/main/data/geojson/ibague_communes.geojson')
      .then(response => response.json())
      .then(data => {
        // Crear la capa de comunas y guardarla
        this.communeLayer = L.geoJSON(data);
        console.log('Capa de comunas cargada correctamente');
      })
      .catch(error => console.error('Error al cargar el GeoJSON de comunas:', error));
  }

  private async loadAllPoints(): Promise<void> {
    if (this.dataLoaded) return;
    this.dataLoaded = true;

    const baseUrl = 'http://localhost:8000/api/v1/biodiversity/records/';
    let currentPage = 1;
    let totalRecords = 0;

    try {
      while (true) {
        // Cargar los registros de la página actual
        const response = await fetch(`${baseUrl}?page=${currentPage}`); // Aquí implementamos la paginación
        const data = await response.json();

        if (!data.count || !data.results || data.results.length === 0) {
          console.warn('No se encontraron registros en la página', currentPage);
          break;
        }

        totalRecords = data.count;
        console.log(`Total de registros hasta la página ${currentPage}: ${totalRecords}`);

        // Procesar los registros de la página actual
        data.results.forEach((record: any) => {
          const lat = record.latitude;
          const lng = record.longitude;

          if (lat && lng) {
            const key = `${lat.toFixed(5)}_${lng.toFixed(5)}`;
            if (!this.loadedPoints.has(key)) {
              this.loadedPoints.add(key);

              const marker = L.circleMarker([lat, lng], {
                radius: 4,
                color: 'black',
                weight: 1,
                fillColor: 'green',
                fillOpacity: 0.5
              }).bindPopup(`
                <b>${record.common_name || 'Sin nombre común'}</b><br>
                <i>${record.species?.scientific_name || 'Sin nombre científico'}</i><br>
                <b>Sitio:</b> ${record.place?.site || 'Sin sitio'}<br>
                <b>Fecha:</b> ${record.date || 'Sin fecha'}
              `);

              // Agregar el marcador al grupo de clusters
              this.markerClusterGroup.addLayer(marker);
            }
          }
        });

        // Si ya hemos cargado todos los registros, salimos del ciclo
        if (data.next === null) {
          console.log('Todos los puntos han sido cargados');
          break;
        }

        // Incrementar la página para cargar la siguiente
        currentPage++;
      }

      console.log('Puntos cargados en el cluster:', this.markerClusterGroup.getLayers().length);

      // Agregar un controlador de capas
      this.addLayerControl();

    } catch (error) {
      console.error('Error al cargar los datos:', error);
    }
  }

  // Función para agregar el controlador de capas
  private addLayerControl(): void {
    const layers = {
      'Puntos de Biodiversidad': this.markerClusterGroup,
      'Comunas de Ibagué': this.communeLayer || new L.LayerGroup() // Usar una capa vacía si la capa de comunas no está cargada aún
    };

    // Crear el control de capas
    L.control.layers(null, layers).addTo(this.map);
  }
}



