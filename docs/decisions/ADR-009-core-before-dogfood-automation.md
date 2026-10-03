# ADR-009: Stabilize EngineeringOS core before autonomous DevControl dogfooding
Status: Accepted

EngineeringOS is an independent engineering-management system. DevControl is its first major dogfood target and one execution substrate, not its architectural parent.

Development sequence:
1. finish the minimum safe EngineeringOS control loop;
2. validate the core without DevControl-specific assumptions;
3. connect DevControl through adapters/evidence contracts;
4. run advisory/shadow dogfood first;
5. progressively authorize bounded actions only after evidence shows the manager/scheduler is reliable.

"Finish" does not mean feature-complete. It means the minimum control loop is coherent, durable, tested, and safe enough to supervise a real project.
