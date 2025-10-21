import { ThemeToggle } from "@/components/theme-toggle";
import { Separator } from "@/components/ui/separator";

export default function AppearancePage() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Appearance</h3>
        <p className="text-sm text-muted-foreground">
          Customize the appearance of the app. Switch between light and dark
          themes.
        </p>
      </div>
      <Separator />
      <div className="flex items-center justify-between rounded-lg border p-4">
        <div className="space-y-0.5">
          <h4 className="font-medium">Theme</h4>
          <p className="text-sm text-muted-foreground">
            Select the theme for the application.
          </p>
        </div>
        <ThemeToggle />
      </div>
    </div>
  );
}
