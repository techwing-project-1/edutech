# CurriculaMind AI Backend

Production-ready AI Backend built with Clean Architecture, SOLID principles, and modular design.

## Folder Architecture

The project strictly follows Clean Architecture:

- **api/**: Presentation Layer. Contains FastAPI routes, dependencies, and controllers.
- **core/**: Core application setups. Settings, configuration, logging, security, and global exception handlers.
- **domain/**: Domain Layer. Core entities, Pydantic schemas, and Interfaces (Abstract Base Classes). Zero external dependencies here.
- **infrastructure/**: Infrastructure Layer. Concrete implementations of external services (LLM Providers, Vector DBs, Relational DBs, PDF Processors).
- **services/**: Application Layer. Business logic, use cases (e.g., RAG pipelines, Orchestration).
- **utils/**: General shared utility functions.

## Future Scalability
This foundation is designed to seamlessly integrate:
- **RAG & Vector DBs**: Through interfaces in `domain/` and concrete integrations in `infrastructure/vector_store/`.
- **LLM Providers**: Abstracted in `infrastructure/llm_providers/`, making it easy to swap OpenAI, Anthropic, or Gemini.
- **PDF Processing**: Handled modularly in `infrastructure/document_parser/`.
- **Prompt Engineering**: Templating engine separated in `services/prompts/`.
