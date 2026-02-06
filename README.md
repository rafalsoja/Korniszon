# Korniszon

![Tests](https://github.com/rafalsoja/Korniszon/actions/workflows/tests.yml/badge.svg)


A simple Docker-based server manager for Minecraft.

###  Features
- [x] Dynamic start/stop of Minecraft server instances via Docker API.
- [ ] Real-time server log streaming to the web console using WebSockets.
- [ ] Mod package management with Modrinth API integration for easy mod selection and installation.

---

## Requirements
- [Docker](https://www.docker.com/)
- [Python 3.13](https://www.python.org/downloads/)
- [OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)

## Installation and Usage

1. Install [Taskfile](https://taskfile.dev/installation/)


2. Install dependencies:
	- Installs applications from [requirements](#requirements)

	```powershell
	task setup:install
	```

3. Generate SSL certificates:

	```powershell
	task certs:gen
	```

4. Run the src:

	```powershell
	task run
	```


