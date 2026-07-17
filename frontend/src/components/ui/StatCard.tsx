import { type HTMLAttributes, forwardRef } from "react";
import { cn } from "@/utils/cn";

interface StatCardProps extends HTMLAttributes<HTMLDivElement> {
  label: string;
  value: string | number;
  change?: number;
}

const StatCard = forwardRef<HTMLDivElement, StatCardProps>(
  ({ label, value, change, className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-xl border border-border bg-surface p-4",
        className
      )}
      {...props}
    >
      <p className="text-xs font-medium text-text-muted uppercase tracking-wider">
        {label}
      </p>
      <p className="mt-1 text-2xl font-bold text-text-primary">{value}</p>
      {change !== undefined && (
        <p
          className={cn(
            "mt-1 text-sm font-medium",
            change >= 0 ? "text-gain" : "text-loss"
          )}
        >
          {change >= 0 ? "+" : ""}
          {change.toFixed(2)}%
        </p>
      )}
    </div>
  )
);
StatCard.displayName = "StatCard";

export { StatCard };
