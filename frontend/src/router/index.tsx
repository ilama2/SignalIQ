import { createBrowserRouter } from "react-router-dom";
import { MainLayout } from "@/components/layout/MainLayout";
import { Dashboard } from "@/pages/Dashboard/Dashboard";
import { Companies } from "@/pages/Companies/Companies";
import { CompanyDetails } from "@/pages/CompanyDetails/CompanyDetails";
import { Recommendations } from "@/pages/Recommendations/Recommendations";
import { Portfolio } from "@/pages/Portfolio/Portfolio";
import { News } from "@/pages/News/News";
import { WatchlistPage } from "@/pages/Settings/Watchlist";
import { Settings } from "@/pages/Settings/Settings";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "companies", element: <Companies /> },
      { path: "companies/:symbol", element: <CompanyDetails /> },
      { path: "recommendations", element: <Recommendations /> },
      { path: "portfolio", element: <Portfolio /> },
      { path: "news", element: <News /> },
      { path: "watchlist", element: <WatchlistPage /> },
      { path: "settings", element: <Settings /> },
    ],
  },
]);
