#! /bin/bash
if [[ -d node_modules/@types/plotly.js ]]; then
  cp -r node_modules/@types/plotly.js node_modules/@types/plotly.js-basic-dist
else
  echo "Plotly type definitions did not exist.";
fi
