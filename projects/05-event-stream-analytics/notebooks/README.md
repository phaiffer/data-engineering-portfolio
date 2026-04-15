# Notebooks

This folder is for lightweight exploratory validation only.

Rules for this project:

- notebooks should inspect landed Bronze or Silver samples;
- reusable pipeline logic belongs in `src/`, not in notebooks;
- notebooks may import helper functions from `src/`;
- notebook cells should stay small and honest.

Environment notes:

- use the project-compatible environment from `requirements.txt`;
- `ipykernel` is included so the environment can be registered as a notebook kernel;
- the notebook bootstrap supports running from repository root, project root, or this folder.
