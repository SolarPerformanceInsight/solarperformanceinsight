# Solar Performance Insight

Solar Performance Insight is an open source platform for evaluating solar power
plant performance. Solar Performance Insight aims to provide an alternative
to available asset modeling tools for PV Operations and Mainteneance (O&M)
providers where existing tools are unaffordable or impractical.

## Platform Layout

The Solar Performance Insight platform has two main components:

### REST API

  The REST API enables programmatic access to Solar Performance Insight
  services. It is built using the [FastAPI](https://fastapi.tiangolo.com/)
  Python web framework. The [pvlib python](https://pvlib-python.readthedocs.io/)
  library provides PV system modeling functionality. Solar Performance
  Insight's data model is defined using
  [pydantic](https://pydantic-docs.helpmanual.io/) (a dependency of FastAPI)
  and provides a translation layer between pvlib's PV system models and
  modeling results and the JSON interface presented by the API.
  Documentation for the development instance of the API can be found at
  [dev.solarperformanceinsight.org/api/docs](https://dev.solarperformanceinsight.org/api/docs).
  Source code can be found in the [api](tree/main/api) directory.

  The API stores metadata and job results in a MySQL database. It uses the [dbmate](https://github.com/amacneil/dbmate)
  migration utility for keeping the database in sync during development.
  Files related to the database and *dbmate* migrations can be found in the
  [db](tree/main/db) directory.

### Web Dashboard

  The web front end provides a graphical interface to the Solar Performance
  Insight services. The front end is built using [Vue.js](https://vuejs.org/). The development
  instance of the dashboard can be found at [dev.solarperformanceinsight.org/](https://dev.solarperformanceinsight.org/).
  Source code can be found in the [dashboard](tree/main/dashboard) directory.
