# Korniszon

![Tests](https://github.com/rafalsoja/Korniszon/actions/workflows/tests.yml/badge.svg)

A simple Docker-based server manager for Minecraft. Actual todo list can be found [here](./docs/todo.md).

### Features

- Backend server management using FastAPI and Docker SDK.
- Real-time server managment using WebSockets.
- Mod package management with Modrinth API integration for easy mod selection and installation.
- SSL certificate generation for secure connections.
- Frontend interface. NYI

---

## Requirements

- [Docker](https://www.docker.com/)
- [Python 3.13](https://www.python.org/downloads/)
- [OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)

## Installation and Usage

1. Install [Taskfile](https://taskfile.dev/installation/)

2. Install dependencies:

   ```powershell
   task setup:install
   ```

3. Generate SSL certificates:

   ```powershell
   task certs:gen
   ```

4. Run the src:

   ```powershell
   task backend:run
   ```
