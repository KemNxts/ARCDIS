# ARCDIS Frontend Dashboard

This is the React + Vite frontend for the ARCDIS (Attack Detection & Prevention System) platform.

## Technologies Used
- React 18 + Vite
- Tailwind CSS
- React Router DOM v6
- Axios
- Recharts
- Lucide React

## Setup & Running

1. **Install Dependencies**
   Navigate to the client directory and install the packages:
   ```bash
   cd client
   npm install
   ```

2. **Environment Configuration**
   Ensure your `.env` file in the `client` directory correctly points to your backend. The default is:
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```

3. **Start the Development Server**
   ```bash
   npm run dev
   ```
   The dashboard will typically be available at `http://localhost:5173`.

## Connecting to the Backend

1. Make sure your FastAPI backend is running (`uvicorn app.main:app --reload` from the backend directory).
2. The frontend uses Axios interceptors to automatically append your JWT token to the `Authorization` header for all requests to the backend.
3. Once running, you can register a new account on the frontend, which will create the user in the backend's MongoDB and log you in.
