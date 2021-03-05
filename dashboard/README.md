# Solar Performance Insight Dashboard

This directory contains the source code for Solar Performance Insight's
Vue.js based dashboard.

## NPM Project Setup
*NOTE:* This project uses the smaller `plotly.js-basic-dist` npm package. To
use the correct types from [definitelytypes](https://github.com/DefinitelyTyped/DefinitelyTyped) we
need to rename the plotly types directory in `node_modules` after install to
make sure Typescript knows where to find the definitions. The `postinstall`
node script will rename this directory appropriately for you.
```
npm install
npm run postinstall
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your unit tests
```
npm run test:unit
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

## Source Directory Structure

- *src/types*
 Directory containing Typescript definitions of the System definition related
 object types defined by the api.

- *src/utils*
 Collection of helper functions and classes for things like displaying
 human friendly variable names, parsing API responses, and unit conversion.

- *src/views*
 Container Vue components to act as targets for the Vue router and nest
 appropriate child components. e.g. the `/systems` listing page.

- *src/components*
 Composable and reusable components.

- *src/components/model*
 Components providing the UI for specifying the System-definition types defined
 in the *src/types* directory.

- *src/components/jobs*
 Components providing UI For specifying, submitting, and viewing job results.
