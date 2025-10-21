import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

export default function ProfileSettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Profile</h3>
        <p className="text-sm text-muted-foreground">
          This is how others will see you on the site. You can update your
          information here.
        </p>
      </div>
      <Separator />
      <form className="space-y-8">
        <div className="grid w-full max-w-sm items-center gap-1.5">
          <Label htmlFor="name">Name</Label>
          <Input id="name" defaultValue="Koichi" />
          <p className="text-sm text-muted-foreground pt-1">
            This will be your public display name.
          </p>
        </div>
        <div className="grid w-full max-w-sm items-center gap-1.5">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" defaultValue="koichi@example.com" />
          <p className="text-sm text-muted-foreground pt-1">
            Your email is not displayed to other users.
          </p>
        </div>
        <Button type="submit">Update profile</Button>
      </form>
    </div>
  );
}
