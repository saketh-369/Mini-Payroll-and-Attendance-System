# 🏢 Mini Payroll & Attendance System

An enterprise-grade, full-stack web application designed to streamline employee management, track attendance, manage leave requests, and automatically calculate dynamic payrolls. Built with a strict **Clean Architecture** pattern, this system implements secure **Role-Based Access Control (RBAC)** to separate administrative powers from employee-level access.

---

## 🌐 Project Details

- **Live Frontend URL:** [https://mini-payroll-and-attendance-system.vercel.app/](https://mini-payroll-and-attendance-system.vercel.app/)
- **Backend API URL:** [https://mini-payroll-and-attendance-system-fxev.onrender.com/](https://mini-payroll-and-attendance-system-fxev.onrender.com/)

### 🔑 Demo Credentials

To explore the system, you can log in to the live frontend using the following administrative credentials:

- **Email:** `admin@test.com`
- **Password:** `Admin@123`

*(As an Admin, you can create new Employee accounts and log in with them to experience the Employee Dashboard).*

---

## 🛠️ Tech Stack

### Frontend
- **React** (Vite)
- **Axios** (Centralized interceptors)
- **Vanilla CSS** (Custom Design System)
- **Vercel** (Cloud Hosting)
- *Features:* Role-based UI rendering, Protected routing, Environment variable-based API configuration.

### Backend
- **FastAPI** (High-performance Python web framework)
- **SQLAlchemy** (ORM)
- **Pydantic** (Data validation & serialization)
- **Render** (Cloud Hosting)
- *Features:* Clean Architecture, JWT Authentication, bcrypt password hashing, Role-Based Access Control (RBAC).

### Database
- **PostgreSQL**
- **Neon Cloud** (Serverless Postgres)

---

## ✨ Core Features & System Modules

### 1. Authentication & Authorization (RBAC)
The system uses a robust **JWT-based stateless authentication** flow. Access to every API endpoint and frontend view is strictly dictated by the user's assigned role.

- **Admin Role:** Can register new employees, view all employee data, approve or reject leave requests, manage bulk attendance, and view payroll across the entire organization.
- **Employee Role:** Securely locked to their own data. They can mark daily attendance, apply for leaves, and view their personal payroll breakdown.

### 2. Employee Management
- **Employee Registration:** Admins can securely register new staff.
- **Role Assignment:** Specify whether a user has `ADMIN` or `EMPLOYEE` privileges.
- **Contract Types:** Support for `Office`, `On-site`, and `WFH` work environments.
- **Salary Configuration:** Define whether the employee is on a `monthly` salary or `daily` wage contract.

### 3. Attendance Management
- **Daily Check-ins:** Employees can mark their attendance daily.
- **Bulk Entry:** Admins can submit batch attendance records for multiple employees simultaneously.
- **Duplicate Prevention:** The database enforces a `UniqueConstraint` on `(employee_id, date)` to prevent accidental double-marking.

### 4. Leave Management
- **Workflow:** Employees submit leave requests → Status defaults to `pending` → Admin reviews and updates status to `approved` or `rejected`.
- **Payroll Integration:** Approved leaves are automatically integrated into the payroll calculation logic.

### 5. Payroll System (Dynamic Calculation Engine)
The system calculates real-time salaries based on the employee's contract type and historical attendance data. **Approved leave days do NOT count as absences and are paid.**

- **Monthly Employees:** 
  - `salary_per_day = monthly_salary / 30`
  - `total_salary = salary_per_day * (present_days + approved_leave_days)`
- **Daily Wage Employees:**
  - `total_salary = daily_wage * (present_days + approved_leave_days)`

---

## 🏗️ Architecture Explanation

### Backend Clean Architecture
The backend is structured to strictly separate concerns, making the codebase highly maintainable, scalable, and testable: `Routes` → `Services` → `Models` → `Database`.

- `app/routes/`: The thin controller layer. Solely responsible for receiving HTTP requests, enforcing RBAC dependencies, and returning HTTP responses.
- `app/services/`: The core business logic layer. Contains all complex data manipulation, payroll math, and database queries.
- `app/models/`: SQLAlchemy ORM classes that map directly to the PostgreSQL database tables.
- `app/schemas/`: Pydantic models for strict request/response data validation.
- `app/auth/`: Centralized security logic containing JWT generation, bcrypt hashing, and FastAPI dependency injection (`get_current_user`).
- `app/db/`: Database configuration and SQLAlchemy engine initialization.
- `app/utils/`: Custom exception handlers and helper functions.

---

## 🔄 Data & Authentication Flow

### Authentication Flow
1. **Login:** User submits email/password.
2. **Verification:** Backend verifies the hash using `bcrypt`.
3. **Token Generation:** A JWT is generated containing the `sub` (user ID) and `role`.
4. **API Access:** Frontend attaches the JWT as a `Bearer` token in the `Authorization` header via an Axios interceptor.
5. **Validation:** FastAPI `Depends()` extracts the token, verifies the signature, and explicitly checks the `role` before allowing route execution.

### Module Data Flow
- **Leave Flow:** Employee submits `POST /leave` → Row created with `pending` → Admin triggers `PUT /leave/{id}` → Status shifts to `approved` → Payroll engine detects status change.
- **Attendance Flow:** Employee submits `POST /attendance` → Database constraint checks for duplicates → Row created.
- **Payroll Flow:** Admin requests `GET /payroll/{id}` → Service fetches `Attendance` count → Service fetches `Leave` count where status is `approved` → Math engine calculates final salary.

---

## 🗄️ Database Design

The PostgreSQL database relies on strict relational integrity:

- **Employees Table:** Stores core user data, bcrypt `password_hash`, and salary configurations.
- **Attendance Table:** Tracks daily presence. Includes a composite `UniqueConstraint` on `employee_id` and `date`. Includes a `ForeignKey` to the Employees table.
- **Leave Table:** Tracks leave requests (`start_date`, `end_date`, `status`). Includes a `ForeignKey` to the Employees table.

---

## 📖 API Documentation

### Auth APIs
- `POST /auth/login` — Authenticates user and returns JWT.
- `POST /auth/register` — *(Admin Only)* Registers a new employee.

### Employee APIs
- `GET /employees` — *(Admin Only)* Retrieves a list of all employees.

### Attendance APIs
- `POST /attendance` — *(Employee Only)* Marks single attendance. Payload: `{"employee_id": 1, "date": "2026-05-01", "status": "present"}`.
- `POST /attendance/bulk` — *(Admin Only)* Batch marks attendance for multiple users.
- `GET /attendance/{employee_id}` — Retrieves attendance records. Employees can only fetch their own ID.

### Leave APIs
- `POST /leave` — *(Employee Only)* Applies for leave. Payload: `{"employee_id": 1, "start_date": "...", "end_date": "..."}`.
- `PUT /leave/{id}` — *(Admin Only)* Approves/Rejects leave. Payload: `{"status": "approved"}`.
- `GET /leave` — Retrieves leaves. Admins see all, Employees only receive their own records.

### Payroll APIs
- `GET /payroll/{employee_id}` — Calculates and returns the JSON payload structure containing `total_days`, `present_days`, `absent_days`, `approved_leave_days`, and final `salary`.

---

## 💻 Frontend Explanation

The React frontend relies on a dynamic, role-based rendering architecture:
- **Axios Configuration:** A centralized instance (`src/api.js`) reads the `VITE_API_URL` from environment variables and automatically injects the JWT into all requests.
- **State Management:** The root `App.jsx` component stores the authenticated user object. 
- **Role-Based Rendering:** UI Tabs (e.g., "Employees" or "Bulk Entry") are conditionally hidden from the DOM if `user.role !== 'ADMIN'`.
- **Protected Routes:** If no JWT is found in `localStorage`, the user is hard-redirected to the Login component.

---

## 🔒 Security Features

1. **Password Hashing:** Passwords are never stored in plain text; they are hashed using `bcrypt` with unique salts.
2. **Stateless Sessions:** JWT tokens eliminate the need for server-side session memory and securely embed the user's role cryptographically.
3. **Endpoint Protection:** Even if an employee bypasses the hidden UI elements on the frontend, the FastAPI backend will reject unauthorized requests with a `403 Forbidden` error.
4. **Environment Variables:** Database credentials and the JWT Secret Key are securely injected via `.env` files and never committed to version control.

---

## 🚀 Deployment

- **Frontend (Vercel):** The Vite React application is deployed via Vercel. The backend URL is injected into the static build via the `VITE_API_URL` environment variable.
- **Backend (Render):** The FastAPI server is hosted on Render as a Web Service.
- **Database (Neon):** The PostgreSQL database runs on Neon's serverless cloud infrastructure.

---

## ⚙️ Local Setup Instructions

### 1. Database & Backend Setup
1. Clone the repository and navigate to the `backend/` folder.
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows).
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file in `backend/` and add:
   ```env
   DATABASE_URL=postgresql://<your_neon_user>:<your_neon_password>@<your_neon_host>/<db_name>?sslmode=require
   SECRET_KEY=your_super_secret_jwt_key
   ```
6. Run the database seed script to generate tables and the default Admin user: `python seed_admin.py`
7. Start the server: `uvicorn app.main:app --reload`

### 2. Frontend Setup
1. Navigate to the `frontend/` folder.
2. Install dependencies: `npm install`
3. Create a `.env` file in `frontend/` and add:
   ```env
   VITE_API_URL=http://localhost:8000
   ```
4. Start the development server: `npm run dev`

---

## 🧪 Testing

Comprehensive End-to-End (E2E) testing was performed using FastAPI's `TestClient` mimicking the entire real-world production lifecycle:
- **RBAC Validation:** Simulated adversarial attacks using Employee tokens to hit Admin endpoints, successfully receiving `403 Forbidden` barriers.
- **Payroll Validation:** Validated that mathematical edge cases (e.g., Approved Leaves acting as paid present days) output accurately down to the decimal point for both Monthly and Daily wage contracts.
- **Database Validation:** Confirmed PostgreSQL `IntegrityError` successfully prevents duplicate attendance entries.

---

## 🔮 Future Improvements

While this MVP is production-ready, future scaling features could include:
- **Date-Bound Payroll Processing:** Updating the payroll engine to calculate logic strictly scoped to a specific `month` and `year`.
- **Set-Based Deduplication:** Enforcing strict calendar date overlap checks between the Attendance and Leave tables to prevent double-dipping.
- **Email Notifications:** Automatic emails to employees when their leave is approved/rejected.
- **Audit Logging:** Tracking exactly which Admin approved a specific payroll or leave request.
- **Analytics Dashboard:** Visualizing attendance trends and payroll expenditures.
