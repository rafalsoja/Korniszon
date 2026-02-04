## Korniszon

A simple Docker-based server manager for Minecraft.

###  Features
- todo

---

## Requirements
- Windows 10 or higher
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.13](https://www.python.org/downloads/)
- [OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)

## Installation and Usage

1. Install Taskfile:

	```powershell
	winget install Task.Task
	```


2. Install dependencies:
	- Installs applications from [requirements](#requirements)

	```powershell
	task install
	```

3. Generate SSL certificates:

	```powershell
	task gen-certs
	```

4. Run the backend:

	```powershell
	task run
	```


