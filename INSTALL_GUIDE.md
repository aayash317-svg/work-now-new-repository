# ⚠️ Action Required: Setup Your Environment

It looks like **Node.js** and **npm** are not installed or not in your system's `PATH`. This is why you see **304+ problems** in your IDE (all imports are failing) and why the commands I gave you failed.

## 1. Install Node.js
Go to **[nodejs.org](https://nodejs.org/)** and download the **LTS (Long Term Support)** version for Windows.
*   Run the installer.
*   **Important**: Make sure "Add to PATH" is checked (it is by default).

## 2. Restart your Terminal / IDE
After installing, you **must close and reopen** VS Code (or your terminal) for it to recognize the new commands.

## 3. Verify Installation
Open a terminal and type:
```bash
node -v
npm -v
```
If you see version numbers (e.g., `v20.x.x`), you are ready!

## 4. Fix the "304 Problems"
Once Node is installed, run these commands in order:

```powershell
# Setup Backend
cd "d:\student job\backend"
npm install

# Setup Frontend
cd "d:\student job\frontend"
npm install
```

---

## 🐋 Optional: Docker
To run the databases (PostgreSQL, Redis) without installing them individually, you should also install **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**.
