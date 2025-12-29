import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import api from "./api";

export default function ProtectedRoute({ children }) {
  const [status, setStatus] = useState("loading"); // loading | authed | unauth

  useEffect(() => {
    api
      .get("/auth/me")
      .then(() => setStatus("authed"))
      .catch(() => setStatus("unauth"));
  }, []);

  if (status === "loading") {
    return <div>Loading...</div>; // or spinner
  }

  if (status === "unauth") {
    return <Navigate to="/login" replace />;
  }

  return children;
}
