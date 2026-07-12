# In-Memory SQL Database - Architecture Overview

This document provides a high-level overview of the in-memory SQL database architecture.

## System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        CLI["Command Line Interface"]
        API["API Interface"]
    end
    
    subgraph Parser["Parser & Execution Layer"]
        Lexer["Lexical Analyzer"]
        SQLParser["SQL Parser"]
        Optimizer["Query Optimizer"]
    end
    
    subgraph Engine["Query Execution Engine"]
        Executor["Query Executor"]
        Planner["Execution Planner"]
    end
    
    subgraph Storage["Storage Layer"]
        Memory["In-Memory Data Store"]
        IndexMgr["Index Manager"]
        Cache["Query Cache"]
    end
    
    subgraph Tables["Data Structures"]
        Table1["Table 1"]
        Table2["Table 2"]
        TableN["Table N"]
    end
    
    subgraph Utils["Utilities"]
        Logger["Logger"]
        Validator["Input Validator"]
    end
    
    CLI -->|SQL Query| Lexer
    API -->|SQL Query| Lexer
    Lexer --> SQLParser
    SQLParser --> Optimizer
    Optimizer --> Executor
    Executor --> Planner
    Planner --> Memory
    Memory --> IndexMgr
    Memory --> Cache
    IndexMgr --> Table1
    IndexMgr --> Table2
    IndexMgr --> TableN
    Validator -.->|Validation| Lexer
    Logger -.->|Logging| Executor
    
    style Client fill:#e1f5ff
    style Parser fill:#f3e5f5
    style Engine fill:#fff3e0
    style Storage fill:#e8f5e9
    style Tables fill:#fce4ec
    style Utils fill:#f1f8e9
```

## Component Descriptions

### Client Layer
- **Command Line Interface**: User-facing CLI for executing SQL commands
- **API Interface**: Programmatic interface for application integration

### Parser & Execution Layer
- **Lexical Analyzer**: Tokenizes SQL input into meaningful units
- **SQL Parser**: Parses tokens into an abstract syntax tree (AST)
- **Query Optimizer**: Optimizes the execution plan for better performance

### Query Execution Engine
- **Query Executor**: Executes the optimized query plan
- **Execution Planner**: Converts optimized query into executable steps

### Storage Layer
- **In-Memory Data Store**: Stores all table data in RAM for fast access
- **Index Manager**: Manages indexes for optimized data retrieval
- **Query Cache**: Caches frequently executed queries for performance

### Data Structures
- **Tables**: Individual table storage with rows and columns

### Utilities
- **Logger**: Logs system operations and debugging information
- **Input Validator**: Validates SQL input before processing

## Data Flow

1. User submits SQL query through CLI or API
2. Lexer tokenizes the query string
3. Parser builds an AST from tokens
4. Optimizer analyzes and optimizes the execution plan
5. Executor runs the optimized plan
6. Results are retrieved from in-memory storage
7. Results are returned to the user

## Key Features

- **In-Memory Storage**: All data resides in memory for O(1) access patterns
- **SQL Support**: Full SQL query parsing and execution
- **Indexing**: Supports efficient data retrieval through indexes
- **Query Caching**: Improves performance for repeated queries
- **CLI & API Interfaces**: Multiple ways to interact with the database
