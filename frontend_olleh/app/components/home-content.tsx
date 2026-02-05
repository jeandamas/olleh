"use client";

import { useAuth } from "~/lib/auth-context";
import { Hero } from "~/components/hero";
import { Pricing } from "~/components/pricing";
import { MembershipStatus } from "~/components/membership-status";
import { Skeleton } from "~/components/ui/skeleton";

export function HomeContent() {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading state
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  // Show membership status for authenticated users
  if (isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-12">
        <MembershipStatus />
      </div>
    );
  }

  // Show hero and pricing for non-authenticated users
  return (
    <>
      <Hero />
      <Pricing />
    </>
  );
}
