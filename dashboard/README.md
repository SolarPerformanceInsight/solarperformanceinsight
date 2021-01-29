# Solar Performance Insight Dashboard

## Project setup
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
