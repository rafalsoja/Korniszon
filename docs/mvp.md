# Korniszon – (MVP)

This project is a web-based, self-hosted Minecraft mod server manager, with local backend and frontend components, and Minecraft servers in Docker containers, with future support for custom modpack creation via Modrinth API.

---

## I. Technical Architecture

The application features a local backend and frontend, alongside dynamic Docker containers for Minecraft server instances. 

| Component | Role / Goal | Technology / Tool |
| :--- | :--- | :--- |
| **Backend API** | The system's brain: business logic, Docker API, Modrinth API, WebSockets. | **Python 3.11+, FastAPI** |
| **Database** | Persistence for configuration, user data, and package states. | **SQLite** |
| **Frontend** | Web Interface (admin panel) for user interaction. | **Vue.js** |
| **MC Instances** | The actual Minecraft server process. | **TemurinJDK** |
| **Orchestration** | Dynamic start/stop of MC servers. | **Docker API** |

---

## II. MVP Features

### A. Infrastructure and Security

1.  **Easy Deployment:** Deploy the backend and frontend locally, while using Docker for Minecraft server management.
2.  **Secure Login:** The web interface is accessible via **HTTPS** to protect administrator credentials.
3.  **Data Persistence:** All configuration data (SQLite) and server files are mapped to **host volumes** to ensure data safety upon container shutdown.

### B. Server Instance Management

1.  **Dynamic Control (Docker API):**
    * **Start/Stop** functions for MC instances, implemented by **dynamically creating and terminating separate Docker containers** via the Backend on demand.
2.  **Real-Time Monitoring:**
    * **WebSockets** are used to stream live server logs (from the dynamic container) to the web console.
3.  **Basic Control:** Ability to send commands to the running Minecraft server console.

### C. Mod Package Management (Modrinth Integration)

1.  **New Package Creation:**
    * The user defines a new instance by selecting the **MC Version** and **Loader**.
    * An integrated **Modrinth search** feature allows the user to browse and select mods to be included in the package.
    * The system automatically downloads the **server engine** and the **selected mod `.jar` files** into the instance directory.
2.  **Import Existing Packages:**
    * Ability to enter a Modrinth Project ID/Slug or link to **automatically download and configure** a pre-made modpack.