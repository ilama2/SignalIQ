import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Building2,
  TrendingUp,
  Briefcase,
  Newspaper,
  Star,
  Settings,
  Activity,
} from "lucide-react";
import { cn } from "@/utils/cn";
import { useSidebar } from "@/contexts/SidebarContext";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/companies", label: "Companies", icon: Building2 },
  { to: "/recommendations", label: "Recommendations", icon: TrendingUp },
  { to: "/portfolio", label: "Portfolio", icon: Briefcase },
  { to: "/news", label: "News", icon: Newspaper },
  { to: "/watchlist", label: "Watchlist", icon: Star },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const { isOpen } = useSidebar();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-border bg-surface transition-all duration-300",
        isOpen ? "w-60" : "w-16"
      )}
    >
      <div className="flex h-14 items-center gap-2 border-b border-border px-4">
        <Activity className="h-6 w-6 shrink-0 text-primary" />
        {isOpen && (
          <span className="text-lg font-bold text-text-primary">SignalIQ</span>
        )}
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-light text-primary"
                  : "text-text-secondary hover:bg-surface-hover hover:text-text-primary",
                !isOpen && "justify-center px-0"
              )
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {isOpen && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border p-4">
        {isOpen && (
          <p className="text-xs text-text-muted">SignalIQ v0.1.0</p>
        )}
      </div>
    </aside>
  );
}
