import React from "react";
import {
  Routes,
  Route,
  Navigate,
  useNavigate,
  useLocation,
} from "react-router-dom";
import ChatPage from "./ChatPage";
import WeeklyPlanPage from "./WeeklyPlanPage";
import LoginPage from "./LoginPage";
import RegisterPage from "./RegisterPage";
import ProtectedRoute from "./ProtectedRoute";
import UserProfilePage from "./UserProfilePage";
import api from "./api";
function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();

  const isPlan = location.pathname.startsWith("/plan");
  const isChat = location.pathname.startsWith("/chat");

  const handleLogout = async () => {
    await api.post("/auth/logout"); // backend deletes cookie
    navigate("/login", { replace: true });
  };

  return (
    <div
      style={{
        display: "flex",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        backgroundColor: "#f5f7fa",
        fontFamily: "sans-serif",
      }}
    >
      <aside
        style={{
          width: "240px",
          backgroundColor: "#1a1c23",
          color: "white",
          display: "flex",
          flexDirection: "column",
          padding: "20px 0",
          zIndex: 1000,
        }}
      >
        <div
          style={{
            padding: "0 20px 30px",
            fontSize: "1.2rem",
            fontWeight: "bold",
            color: "#3b82f6",
          }}
        >
          BODYBUILDER AI
        </div>

        <nav style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
          <button
            onClick={() => navigate("/profile")}
            style={sidebarBtnStyle(location.pathname.startsWith("/profile"))}
          >
            👤 User Profile
          </button>
          <button
            onClick={() => navigate("/plan")}
            style={sidebarBtnStyle(isPlan)}
          >
            📅 每週訓練計畫
          </button>
          <button
            onClick={() => navigate("/chat")}
            style={sidebarBtnStyle(isChat)}
          >
            💬 AI 健身助手
          </button>

          <div style={{ marginTop: "auto", padding: "0 20px" }}>
            <button
              onClick={handleLogout}
              style={{ ...sidebarBtnStyle(false), width: "100%" }}
            >
              🚪 Logout
            </button>
          </div>
        </nav>
      </aside>

      <main
        style={{
          flex: 1,
          position: "relative",
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {children}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected */}
      <Route
        path="/plan"
        element={
          <ProtectedRoute>
            <Layout>
              <WeeklyPlanPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <Layout>
              <ChatPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Layout>
              <UserProfilePage />
            </Layout>
          </ProtectedRoute>
        }
      />
      {/* Default: land on plan, ProtectedRoute will bounce to login if no token */}
      <Route path="/" element={<Navigate to="/plan" replace />} />

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

const sidebarBtnStyle = (active) => ({
  padding: "15px 25px",
  textAlign: "left",
  border: "none",
  background: active ? "#2d3748" : "transparent",
  color: active ? "#3b82f6" : "#cbd5e0",
  cursor: "pointer",
  fontSize: "0.95rem",
  fontWeight: "600",
  borderLeft: active ? "4px solid #3b82f6" : "4px solid transparent",
  transition: "0.2s",
});
