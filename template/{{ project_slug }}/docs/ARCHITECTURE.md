# Architecture

This scaffold follows a data-centric state machine with Prefect orchestration and a clear separation of concerns:

- Schemas as contracts for data boundaries
- Tasks group into flows representing state transitions (ingest→validate→feature→train→deploy)
- Prefect coordinates local execution and can later target remote infrastructure

Two-plane setup:

- Template plane: structure, conventions, starter flows/CLI
- Library plane (`mlcore`): reusable utilities (logging, IO, model cards). Projects pin an upper bound and can swap a local path during development.
