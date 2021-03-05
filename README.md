# Solar Performance Insight

Solar Performance Insight is an open source platform for evaluating solar power
plant performance. Solar Performance Insight aims to provide a tool for the PV
Operations and Mainteneance (O&M) community to compare actual plant
performance with modeled performance.

# Platform Layout

The Solar Performance Insight platform has two main components:

- *REST API*
 A REST API to enable programmatic access to Solar Performance Insight
 services that is built using [FastAPI](https://fastapi.tiangolo.com/).
 Documentation for the development instance of the API can be found at
 [dev.solarperformanceinsight.org/api/docs](https://dev.solarperformanceinsight.org/api/docs).
 Source code can be found in the [api](tree/main/api)` directory.

 The API utilizes a MySQL database for storage and uses the [dbmate](https://github.com/amacneil/dbmate)
 migration utility for keeping the database in sync during development.
 Files related to the database and *dbmate* migrations can be found in the
 [db](tree/main/db) directory.

- *Web Dashboard*
 Web front end provides a graphical interface to the Solar Performance
 Insight services build using [Vue.js](https://vuejs.org/).The development
 instance of the dashboard can be found at [dev.solarperformanceinsight.org/](https://dev.solarperformanceinsight.org/).
 Source code can be found in the [dashboard](tree/main/dashboard) directory.
