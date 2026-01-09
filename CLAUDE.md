# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Entangle is a Python data synchronization tool that transfers data between external systems (MySQL/Oracle) and a scientific research management system (科研系统). It uses Redis as a message queue for tracking changes with MD5-based change detection.

## Common Commands

### Running the Application

```bash
# Sync external data to research system (scheduled, runs every core.period seconds)
python -m entangle -c ../etc/config.yml cmd0

# Incremental sync for a specific table
python -m entangle -c ../etc/config.yml cmd1 -n TABLE_NAME

# Full copy sync for a specific table
python -m entangle -c ../etc/config.yml cmd2 -n TABLE_NAME

# Sync research system data to external Oracle database
python -m entangle -c ../etc/config.yml cmd3

# Process historical data
python -m entangle -c ../etc/config.yml -s cmd2
```

### Building and Packaging

```bash
# Create executable archive
python -m zipapp src -o entangle.pyz

# Docker image
docker build --force-rm -t spms/entangle -f Dockerfile .

# Run with Docker Compose
docker-compose start spmsin  # sync to research system
docker-compose start spmsout # sync to finance system
```

### Testing

```bash
# Run tests from project root
pytest test/
```

## Architecture

### Command Structure
- **cmd0** (`api/cmd0.py`): Scheduler that runs periodically, dispatches to cmd1 or cmd2 based on table configuration mode
- **cmd1** (`api/cmd1.py`): Incremental sync - detects changes using MD5 hashes stored in Redis, pushes change events (insert/update/delete) to Redis queues
- **cmd2** (`api/cmd2.py`): Full copy sync - replaces entire dataset in Redis. Supports `forward` mode for bulk JSON transfer
- **cmd3** (`api/cmd3.py`): Reverse sync - consumes Redis queue messages and writes to Oracle using MERGE statements

### Key Modules
- `core/config.py`: YAML configuration loader, accessed via `config.*` attributes
- `core/logger.py`: Logging setup with YAML-based configuration
- `api/resource.py`: Database connection factories (MySQL, Oracle, Redis)
- `api/glovar.py`: Global exit flag for graceful shutdown on SIGINT/SIGTERM

### Configuration (`etc/config.yml`)

Table sync is configured under `entangle:` section. Each table entry defines:
- `source`: Database source (`mysql` or `oracle`)
- `mode`: Sync mode (`copy` for cmd2, otherwise cmd1 incremental)
- `target`: Redis key prefix for storing data
- `pk`: Primary key columns
- `fields`: Column mapping from source to target field names
- `condition`: Optional WHERE clause filter
- `rules`: Optional value transformation mappings

### Data Flow
1. **Inbound sync (cmd0/cmd1/cmd2)**: External DB → Redis queues/hashes
2. **Outbound sync (cmd3)**: Redis queue → Oracle (via MERGE upsert)

Redis keys follow pattern `{target}:{pk_value}` for records, `{target}` for queues/sets.
