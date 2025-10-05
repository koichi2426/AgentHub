"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";

// 設定項目のリスト
const sidebarNavItems = [
  {
    title: "Profile",
    href: "/settings", // 将来的に実装
  },
  {
    title: "Appearance",
    href: "/settings/appearance",
  },
  {
    title: "Account",
    href: "/settings/account", // 将来的に実装
  },
];

export function SettingsSidebar() {
  const pathname = usePathname();

  return (
    <nav className="flex space-x-2 lg:flex-col lg:space-x-0 lg:space-y-1">
      {sidebarNavItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            buttonVariants({ variant: "ghost" }),
            pathname === item.href
              ? "bg-muted hover:bg-muted"
              : "hover:bg-transparent hover:underline",
            "justify-start"
          )}
        >
          {item.title}
        </Link>
      ))}
    </nav>
  );
}
