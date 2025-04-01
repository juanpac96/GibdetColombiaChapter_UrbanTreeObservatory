FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install --legacy-peer-deps

# Copy project files
COPY . .

# Create Angular workspace if it doesn't exist
RUN if [ ! -f "angular.json" ]; then \
      echo '{ "version": 1, "cli": { "cache": { "enabled": true, "path": ".angular/cache", "environment": "all" } }, "projects": { "urban-tree-observatory": { "projectType": "application", "root": "", "sourceRoot": "src", "architect": { "build": { "builder": "@angular-devkit/build-angular:browser", "options": { "outputPath": "dist", "index": "src/index.html", "main": "src/main.ts", "polyfills": "src/polyfills.ts", "tsConfig": "tsconfig.json", "assets": ["src/assets"], "styles": ["src/styles.css"], "scripts": [] } } } } } }' > angular.json && \
      mkdir -p src/app && \
      echo 'import { NgModule } from "@angular/core"; import { BrowserModule } from "@angular/platform-browser"; import { AppComponent } from "./app.component"; @NgModule({ declarations: [AppComponent], imports: [BrowserModule], providers: [], bootstrap: [AppComponent] }) export class AppModule { }' > src/app/app.module.ts && \
      echo 'import { Component } from "@angular/core"; @Component({ selector: "app-root", template: "<h1>Urban Tree Observatory</h1><p>Application is loading...</p>" }) export class AppComponent { }' > src/app/app.component.ts && \
      echo '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Urban Tree Observatory</title><base href="/"></head><body><app-root></app-root></body></html>' > src/index.html && \
      echo 'import { enableProdMode } from "@angular/core"; import { platformBrowserDynamic } from "@angular/platform-browser-dynamic"; import { AppModule } from "./app/app.module"; platformBrowserDynamic().bootstrapModule(AppModule).catch(err => console.error(err));' > src/main.ts && \
      echo 'import "zone.js";' > src/polyfills.ts && \
      echo 'body { font-family: Arial, sans-serif; margin: 20px; }' > src/styles.css && \
      echo '{ "compileOnSave": false, "compilerOptions": { "baseUrl": "./", "outDir": "./dist/out-tsc", "sourceMap": true, "declaration": false, "downlevelIteration": true, "experimentalDecorators": true, "moduleResolution": "node", "importHelpers": true, "target": "es2015", "module": "es2020", "lib": ["es2018", "dom"] } }' > tsconfig.json; \
    fi

# Expose port
EXPOSE 4200

# Start development server with host set to 0.0.0.0 to allow external access
CMD ["npm", "start", "--", "--host", "0.0.0.0"]
