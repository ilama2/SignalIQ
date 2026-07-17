import { type HTMLAttributes, forwardRef } from "react";
import { cn } from "@/utils/cn";

interface StockPriceProps extends HTMLAttributes<HTMLDivElement> {
  price: number;
  change: number;
  changePercent: number;
  size?: "sm" | "md" | "lg";
}

const StockPrice = forwardRef<HTMLDivElement, StockPriceProps>(
  ({ price, change, changePercent, size = "md", className, ...props }, ref) => {
    const isPositive = change >= 0;

    const sizeClasses = {
      sm: "text-sm",
      md: "text-base",
      lg: "text-xl",
    };

    return (
      <div ref={ref} className={cn("flex items-baseline gap-2", className)} {...props}>
        <span className={cn("font-semibold text-text-primary", sizeClasses[size])}>
          {price.toFixed(2)}
        </span>
        <span
          className={cn(
            "font-medium",
            isPositive ? "text-gain" : "text-loss",
            size === "lg" ? "text-sm" : "text-xs"
          )}
        >
          {isPositive ? "+" : ""}
          {change.toFixed(2)} ({isPositive ? "+" : ""}
          {changePercent.toFixed(2)}%)
        </span>
      </div>
    );
  }
);
StockPrice.displayName = "StockPrice";

export { StockPrice };
