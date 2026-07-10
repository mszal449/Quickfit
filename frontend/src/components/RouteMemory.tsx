import { useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { readLastRoute, saveLastRoute } from "../lib/lastRoute";

const RESTORE_FROM = ["/", "/dashboard"];
const SKIP_SAVE = ["/", "/login"];

export function RouteMemory() {
  const location = useLocation();
  const navigate = useNavigate();
  const restored = useRef(false);

  useEffect(() => {
    if (restored.current) return;
    restored.current = true;
    if (!RESTORE_FROM.includes(location.pathname)) return;
    const last = readLastRoute();
    if (last && last !== location.pathname + location.search) {
      navigate(last, { replace: true });
    }
  }, [location.pathname, location.search, navigate]);

  useEffect(() => {
    if (SKIP_SAVE.includes(location.pathname)) return;
    const current = location.pathname + location.search;
    const save = () => saveLastRoute(current);
    save();
    const saveWhenHidden = () => {
      if (document.visibilityState === "hidden") save();
    };
    document.addEventListener("visibilitychange", saveWhenHidden);
    window.addEventListener("pagehide", save);
    return () => {
      document.removeEventListener("visibilitychange", saveWhenHidden);
      window.removeEventListener("pagehide", save);
    };
  }, [location.pathname, location.search]);

  return null;
}
