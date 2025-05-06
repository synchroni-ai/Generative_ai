graph TD
    subgraph FastAPI Application
        A[API Endpoints]
        B[WebSocket Handler]
        C[Middleware: CORS]
    end

    subgraph Database
        D[MongoDB]
        D1[Collection: test_case_generation]
    end

    subgraph Task Queue
        E[Celery]
        F[Worker]
    end

    subgraph File Management
        G[Input Directory]
        H[Output Directory]
        I[Excel Files Directory]
    end

    subgraph Utilities
        J[data_ingestion]
        K[test_case_utils]
        L[user_story_utils]
        M[LLMs: Mistral, OpenAI, LLaMA]
    end

    subgraph Environment Configuration
        N[.env Variables]
    end

    A -->|Fetch/Store| D1
    A -->|Trigger| E
    A -->|Fetch| H
    A -->|Download| I
    A -->|Manage| G
    B --> F
    C --> A

    E --> F
    D --> A
    D --> F

    F --> G
    F --> H
    F --> I

    J --> F
    K --> F
    L --> F
    M --> F

    N --> A
    N --> G
    N --> H
    N --> I