# ADR-008: Parallel work uses renewable leases, not permanent task locks
Status: Accepted

EngineeringOS coordinates AI workers with expiring leases. Permanent locks are unsafe under agent crashes, abandoned chats, network loss, and interrupted tool sessions. Lease expiry permits recovery while stable work-item identity prevents accidental duplicate ownership.

Task closure is evidence-gated and independently verified; an executor's completion claim is not sufficient evidence by itself.
