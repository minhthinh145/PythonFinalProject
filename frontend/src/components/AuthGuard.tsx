import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAppSelector } from "../app/store";
import { selectAuth } from "../features/auth/authSlice";

interface AuthGuardProps {
  children: ReactNode;
  requiredRole: string;
}

export function AuthGuard({ children, requiredRole }: AuthGuardProps) {
  const { user, token } = useAppSelector(selectAuth);


  if (!token) {
    return <Navigate to="/" replace />;
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  if (user.loaiTaiKhoan !== requiredRole) {

    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
