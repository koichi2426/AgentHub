"use client";

import Link from "next/link";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface UserProfileCardProps {
  isLoading: boolean;
  error: string | null;
  user: {
    name: string;
    email: string;
    avatar_url?: string;
  } | null;
}

export function UserProfileCard({ isLoading, error, user }: UserProfileCardProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-3 items-center border rounded-lg p-4 w-full animate-pulse">
        <div className="h-16 w-16 rounded-full bg-muted"></div>
        <div className="h-4 bg-muted rounded w-3/4 mt-3"></div>
        <div className="h-3 bg-muted rounded w-1/2 mt-2"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-3 items-center border rounded-lg p-4 text-center text-sm text-destructive">
        <p>{error}</p>
        <Link href="/login" className="font-bold underline hover:no-underline">
          Login
        </Link>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex flex-col gap-3 items-center border rounded-lg p-4">
      <Avatar className="w-16 h-16 border">
        <AvatarImage src={user.avatar_url} alt={user.name} />
        <AvatarFallback>{user.name.charAt(0).toUpperCase()}</AvatarFallback>
      </Avatar>
      <div className="text-center">
        <h3 className="font-semibold">{user.name}</h3>
        <p className="text-xs text-muted-foreground break-all">{user.email}</p>
      </div>
    </div>
  );
}
