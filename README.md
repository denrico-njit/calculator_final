# FastAPI Calculator with User Authentication (Final Submission)

A FastAPI application with user authentication (JWT), BREAD calculation endpoints, a PostgreSQL backend, full test suite, and a CI/CD pipeline that builds, scans, and deploys a Docker image.

**Docker Hub:** https://hub.docker.com/r/de269/module14

---

## Running the Tests

Make sure you have a PostgreSQL instance running (see Docker setup below) and your virtual environment activated.

```bash
# Unit tests
pytest tests/unit/

# Integration tests (requires PostgreSQL)
pytest tests/integration/

# End-to-end tests (requires the app to be running)
pytest tests/e2e/

# All tests with coverage (excluding e2e)
pytest --ignore=tests/e2e --cov=app --cov=main --cov-report=term-missing
```

The `DATABASE_URL` environment variable must be set for integration and e2e tests:

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db
```

Or use Docker Compose to spin up the full stack:

```bash
docker compose up
```

---

## Integration Tests

Integration tests cover the full request/response cycle against a real PostgreSQL database. Each test gets an isolated session that is truncated after the test runs.

**Calculator and page routes** (`tests/integration/test_fastapi_calculator.py`):
- `GET /health` — health check
- `GET /`, `/register`, `/login`, `/dashboard` — page routes return 200
- `POST /add`, `/subtract`, `/multiply`, `/divide`, `/power` — basic calculator operations
- `POST /divide` with `b=0` — divide by zero error

**Auth endpoints** (`tests/integration/test_auth_endpoints.py`):
- `POST /auth/register` — successful registration, duplicate user, password mismatch, weak password, missing uppercase/lowercase/digit/special character
- `POST /auth/login` — successful login, wrong password, non-existent user, login with email
- `POST /auth/token` — form-based login (Swagger UI), valid and invalid credentials

**Calculation endpoints** (`tests/integration/test_calculation_endpoints.py`):
- `POST /calculations` — add calculation, divide by zero, unauthenticated request
- `GET /calculations` — browse all calculations for current user, empty list
- `GET /calculations/{id}` — read specific calculation, not found
- `PUT /calculations/{id}` — edit calculation, power operation, divide by zero, not found
- `DELETE /calculations/{id}` — delete calculation and verify removal, not found

Run with coverage:

```bash
pytest --cov=app --cov=main --cov-report=term-missing -v
```

---

## E2E Tests

End-to-end tests use Playwright to drive a real browser against a running server. The server must be running before these tests execute.

**Dashboard BREAD operations** (`tests/e2e/test_dashboard_e2e.py`):
- Add a calculation via the form — row appears in the table
- Browse calculations created via API — appear on page load
- Edit a calculation via the modal — row updates in place
- Delete a calculation — row disappears
- Visit `/dashboard` without a token — redirects to `/login`
- Add a power calculation — row appears with correct result
- Add with divide by zero — client-side error, no submission
- Edit with divide by zero — client-side error in the modal

**Auth and calculator** (`tests/e2e/test_e2e.py`):
- Calculator add, power, and divide by zero on the home page
- Register success and short password error
- Login success and wrong password error

Run E2E tests:

```bash
pytest tests/e2e/ -v -m e2e
```

---

## Manual Testing via OpenAPI (Swagger UI)

1. Start the server:

```bash
uvicorn main:app --reload
```

2. Open **http://127.0.0.1:8000/docs** in your browser.

3. Register a user — expand `POST /auth/register`, click **Try it out**, and submit:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "username": "johndoe",
  "password": "SecurePass1!",
  "confirm_password": "SecurePass1!"
}
```

4. Authenticate — click the **Authorize** button at the top of the page, enter your username and password, and click **Authorize**. This stores the JWT token for all subsequent requests.

5. Test the calculation endpoints — expand any `/calculations` route, click **Try it out**, and submit a request. For example, `POST /calculations`:

```json
{
  "a": 10,
  "b": 5,
  "operation": "add"
}
```

You can also view the auto-generated API schema at **http://127.0.0.1:8000/redoc**.

---

# 📦 Project Setup

---

# 🧩 1. Install Homebrew (Mac Only)

> Skip this step if you're on Windows.

Homebrew is a package manager for macOS.  
You’ll use it to easily install Git, Python, Docker, etc.

**Install Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Verify Homebrew:**

```bash
brew --version
```

If you see a version number, you're good to go.

---

# 🧩 2. Install and Configure Git

## Install Git

- **MacOS (using Homebrew)**

```bash
brew install git
```

- **Windows**

Download and install [Git for Windows](https://git-scm.com/download/win).  
Accept the default options during installation.

**Verify Git:**

```bash
git --version
```

---

## Configure Git Globals

Set your name and email so Git tracks your commits properly:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Confirm the settings:

```bash
git config --list
```

---

## Generate SSH Keys and Connect to GitHub

> Only do this once per machine.

1. Generate a new SSH key:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

(Press Enter at all prompts.)

2. Start the SSH agent:

```bash
eval "$(ssh-agent -s)"
```

3. Add the SSH private key to the agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy your SSH public key:

- **Mac/Linux:**

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

- **Windows (Git Bash):**

```bash
cat ~/.ssh/id_ed25519.pub | clip
```

5. Add the key to your GitHub account:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click **New SSH Key**, paste the key, save.

6. Test the connection:

```bash
ssh -T git@github.com
```

You should see a success message.

---

# 🧩 3. Clone the Repository

Now you can safely clone the course project:

```bash
git clone <repository-url>
cd <repository-directory>
```

---

# 🛠️ 4. Install Python 3.10+

## Install Python

- **MacOS (Homebrew)**

```bash
brew install python
```

- **Windows**

Download and install [Python for Windows](https://www.python.org/downloads/).  
✅ Make sure you **check the box** `Add Python to PATH` during setup.

**Verify Python:**

```bash
python3 --version
```
or
```bash
python --version
```

---

## Create and Activate a Virtual Environment

(Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

---

# 🐳 5. (Optional) Docker Setup

> Skip if Docker isn't used in this module.

## Install Docker

- [Install Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

## Build Docker Image

```bash
docker build -t <image-name> .
```

## Run Docker Container

```bash
docker run -it --rm <image-name>
```

---

# 🚀 6. Running the Project

- **Without Docker**:

```bash
python main.py
```

(or update this if the main script is different.)

- **With Docker**:

```bash
docker run -it --rm <image-name>
```

---

# 📝 7. Submission Instructions

After finishing your work:

```bash
git add .
git commit -m "Complete Module X"
git push origin main
```

Then submit the GitHub repository link as instructed.

---

# 🔥 Useful Commands Cheat Sheet

| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Install Homebrew (Mac)          | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Install Git                     | `brew install git` or Git for Windows installer |
| Configure Git Global Username  | `git config --global user.name "Your Name"`      |
| Configure Git Global Email     | `git config --global user.email "you@example.com"` |
| Clone Repository                | `git clone <repo-url>`                          |
| Create Virtual Environment     | `python3 -m venv venv`                           |
| Activate Virtual Environment   | `source venv/bin/activate` / `venv\Scripts\activate.bat` |
| Install Python Packages        | `pip install -r requirements.txt`               |
| Build Docker Image              | `docker build -t <image-name> .`                |
| Run Docker Container            | `docker run -it --rm <image-name>`               |
| Push Code to GitHub             | `git add . && git commit -m "message" && git push` |

---

# 📋 Notes

- Install **Homebrew** first on Mac.
- Install and configure **Git** and **SSH** before cloning.
- Use **Python 3.10+** and **virtual environments** for Python projects.
- **Docker** is optional depending on the project.

---

# 📎 Quick Links

- [Homebrew](https://brew.sh/)
- [Git Downloads](https://git-scm.com/downloads)
- [Python Downloads](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [GitHub SSH Setup Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
