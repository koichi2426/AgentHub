import { Separator } from "@/components/ui/separator";
import { SettingsSidebar } from "@/components/settings-sidebar";

// メタデータは子ページで定義するため、ここでは省略
// export const metadata: Metadata = { ... };

interface SettingsLayoutProps {
  children: React.ReactNode;
}

export default function SettingsLayout({ children }: SettingsLayoutProps) {
  return (
    <div className="container mx-auto max-w-5xl space-y-6 p-10">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">
          Manage your account and appearance settings.
        </p>
      </div>
      <Separator />
      <div className="flex flex-col space-y-8 lg:flex-row lg:space-x-12 lg:space-y-0">
        <aside className="-mx-4 lg:w-1/5">
          <SettingsSidebar />
        </aside>
        <div className="flex-1 lg:max-w-4xl">{children}</div>
      </div>
    </div>
  );
}
