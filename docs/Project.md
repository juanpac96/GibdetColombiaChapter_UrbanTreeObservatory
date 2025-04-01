# Urban Tree Observatory: Data-Driven Monitoring & Conservation in Ibagué, Colombia

**Start Date:** March 28, 2025

![Omdena feature image](https://v5.airtableusercontent.com/v3/u/39/39/1742709600000/eSEpsPtfAvlKLChDHJ9vkg/JVDMnPuAmdU579fucwEMQT7LCMQGNkmSg7PAxmuYzcwJZ5mPysl3-wocFiCeQbtgS5VBr7EML1uLknIVUu8ghzQq-CN6rtOlVu7-dNcBJwemtHyadntndlKJCMWVoHNtUmAaF9acg0FsXE9TQ4oxJQ/r5puAWg6oO4-d46_ZUr0Ln5nsAa6iC18tBx4maG5mpM)

## Challenge Background

Urban trees provide essential environmental, social, and economic benefits, including air purification, temperature regulation, biodiversity support, and aesthetic value. However, many cities, including Ibagué, Colombia, lack an updated and public monitoring system for their urban and rural trees.

The absence of structured data on tree species, health status, threats, and maintenance history leads to poor decision-making in urban planning and conservation efforts.

Additionally, without a publicly accessible platform, citizens have limited ways to report concerns about trees at risk, whether due to disease, improper pruning, or urban expansion. A robust digital platform can empower decision-makers, researchers, and citizens by providing real-time, data-driven insights into the status of the urban and rural tree population in Ibagué.

## The Problem

Currently, Ibagué lacks a centralized, interactive, and public tree monitoring system. The challenges include:

- **Fragmented Data:** Information on trees is scattered across different municipal and environmental agencies.
- **Lack of Citizen Engagement:** No existing platform allows residents to report tree-related concerns.
- **Limited Tracking of Conservation Efforts:** There is no system for tracking inspections, pruning, or interventions over time.

## Goal of the Project

The goal of this project is to develop an interactive and data-driven platform to monitor urban and rural trees in Ibagué, Colombia. The platform will:

- Map and display the most updated tree database with species, locations, and health conditions.
- Allow citizens to report damaged, diseased, or missing trees.
- Track inspections and interventions over time.
- Analyze environmental impact, including flowering and fruiting seasons.
- Host an API to allow external integrations.

## Project Timeline

### 1. Data Collection and Structuring Tree Database

- Gather data from public records, environmental agencies, and field surveys.
- Clean and preprocess data (removing duplicates, standardizing formats).
- Set up PostgreSQL + PostGIS database for geospatial data storage.

### 2. Exploratory Data Analysis (EDA) & GIS Mapping

- Perform EDA to analyze species distribution, tree health, and density.
- Integrate GIS tools (Leaflet/Mapbox) to visualize tree locations.
- Define and document key attributes for tree classification.

### 3. Building REST API for Data Access

- Develop Django REST API to serve tree data.
- Implement endpoints for querying trees by location, species, and health status.
- Set up authentication and user roles (admin, researchers, public users).

### 4. Developing Front-end

- Build Angular UI with interactive maps.
- Allow users to search, filter, and report tree conditions.
- Integrate the REST API with the frontend for dynamic updates.

## What You'll Learn

This project involves a combination of GIS, data science, software engineering, and environmental monitoring. Team members will gain experience in:

- **Data Collection:** Gathering and structuring tree-related data from public and government sources.
- **Geospatial Analysis:** Using PostGIS and GIS libraries to map tree locations.
- **Machine Learning:** Implementing predictive models for tree health assessment.
- **API Development:** Creating a REST API to share data with third-party applications.
- **Web Development:** Building a Django + Angular platform for real-time monitoring.
- **Cloud Deployment:** Hosting the platform on Kubernetes or cloud-based infrastructure.
