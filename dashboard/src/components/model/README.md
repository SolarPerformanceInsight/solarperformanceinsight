# Model Components
These Vue components provide a user interface for defining a Solar Performance
Insight system specification. Each file contains a component for editing one of
the classes defined in `src/types` from the system metadata specification. The
root component can be found in `System.vue`.

It should be noted that these components modify their props directly, since the
intent of these components is edit or generate a single JSON system
specification to send to the API.
