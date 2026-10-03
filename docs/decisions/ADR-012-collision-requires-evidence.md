# ADR-012: Active-line collision requires evidence
Status: Accepted

EngineeringOS will not block work merely because another development line or workspace is dirty. It must establish overlap through mutation surface, dependency/contract relationship, ownership/lease, or another explicit conflict signal.

When a planned mutation overlaps an active dirty line, the default scheduler state is `BLOCKED_BY_ACTIVE_LINE` and the required action is isolation or waiting. Clearance based only on exact paths remains provisional when semantic contracts overlap.
