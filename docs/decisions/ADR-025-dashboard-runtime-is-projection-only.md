# ADR-025: Dashboard runtime data is projection-only
Status: Accepted

Control Room runtime files are generated from EngineeringOS durable state and are not an independent state store. They are excluded from source control and may be regenerated at any time.

The dashboard may display policy/approval/execution state but cannot manufacture or persist an independent approval decision. Future dashboard actions must enter the same policy + command processor boundary used by agents.
