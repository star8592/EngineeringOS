# Control Room Serving

During G2/G3 dogfood the Human Control Room is served as a localhost-only, read-only projection at `http://127.0.0.1:8777/`.

The preview server is not an authority and exposes no mutation or approval API. `POST`, `PUT`, `PATCH`, and `DELETE` are rejected. Runtime JSON is regenerated from `.engineeringos` durable state. This preserves ADR-023 and ADR-025: there is one policy/approval authority and the UI is projection-only.

The current Python HTTP service is a dogfood serving adapter. The long-term serving endpoint belongs behind the Rust control-plane/API boundary once that boundary becomes authoritative; the dashboard state contract does not depend on this server implementation.
