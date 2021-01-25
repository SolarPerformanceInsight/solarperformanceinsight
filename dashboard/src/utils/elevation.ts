/* istanbul ignore file */
/* Loads the google maps api and makes requests for elevations at a specific lat/lon
 *
 */
import { Loader } from "@googlemaps/js-api-loader";

// @ts-expect-error
const apiKey: string = process.env.VUE_APP_GOOGLE_MAPS_API_KEY;

/**
 * Lazy loads the google maps library and requests the elevation at a lat/lon.
 * @param {number} lat - Latitude (-90, 90)
 * @param {number} lng - Longitude (-180, 180)
 * @param {function} callback - Callback to be called with the results of the
 *   elevation request that takes the parameters:
 *     results: Array<ElevationResults> - Length one array where elevation can
 *       be found in the elevation property of results[0].
 *     status: string - Status of the request. will be "OK" on success.
 *
 * Extra information on these Google Maps Javascript API methods can be found
 * here: https://developers.google.com/maps/documentation/javascript/elevation#ElevationRequests
 */
export function getElevation(
  lat: number,
  lng: number,
  callback: (results: any, status: any) => void
) {
  const loader = new Loader({
    apiKey: apiKey,
    version: "weekly"
  });
  loader.load().then(() => {
    const elevator = new google.maps.ElevationService();

    elevator.getElevationForLocations(
      { locations: [{ lat: lat, lng: lng }] },
      callback
    );
  });
}
