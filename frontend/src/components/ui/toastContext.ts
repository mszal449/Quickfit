import { createContext } from "react";

export type Tone = "error" | "success" | "info";

export interface ToastApi {
  show: (message: string, tone?: Tone) => void;
  error: (message: string) => void;
  success: (message: string) => void;
}

export const ToastContext = createContext<ToastApi | null>(null);
