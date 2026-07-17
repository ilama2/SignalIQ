import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Settings as SettingsIcon } from "lucide-react";

export function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Settings</h1>
        <p className="text-sm text-text-secondary">Manage your account preferences</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5" />
            Profile
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 max-w-md">
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Name</label>
              <Input defaultValue="Investor" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Email</label>
              <Input defaultValue="investor@example.com" type="email" />
            </div>
            <Button>Save Changes</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 max-w-md">
            <div className="flex items-center justify-between rounded-lg border border-border p-4">
              <div>
                <p className="text-sm font-medium text-text-primary">Dark Mode</p>
                <p className="text-xs text-text-muted">Enabled by default</p>
              </div>
              <div className="h-6 w-11 rounded-full bg-primary p-0.5">
                <div className="h-5 w-5 translate-x-5 rounded-full bg-white" />
              </div>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-border p-4">
              <div>
                <p className="text-sm font-medium text-text-primary">
                  Email Notifications
                </p>
                <p className="text-xs text-text-muted">
                  Receive daily market summaries
                </p>
              </div>
              <div className="h-6 w-11 rounded-full bg-surface-hover p-0.5">
                <div className="h-5 w-5 rounded-full bg-text-muted" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
