"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "~/lib/auth-context";
import { membershipApi } from "~/lib/membership";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { CircleCheck } from "lucide-react";
import { cn } from "~/lib/utils";
import { Separator } from "~/components/ui/separator";
import { Skeleton } from "~/components/ui/skeleton";
import { useNavigate } from "react-router";

interface PricingProps {
  heading?: string;
  description?: string;
  className?: string;
}

const Pricing = ({
  heading = "Choose Your Membership",
  description = "Select an annual membership plan to get started with OLLEH. All memberships are valid for one year.",
  className,
}: PricingProps) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Fetch available memberships
  const { data: memberships, isLoading } = useQuery({
    queryKey: ['memberships', 'available'],
    queryFn: membershipApi.getAvailableMemberships,
    retry: false,
  });

  const handleGetStarted = (membershipId?: number) => {
    if (isAuthenticated) {
      // If authenticated, navigate to home where they'll see membership status
      navigate('/');
    } else {
      // If not authenticated, navigate to signup
      navigate('/signup');
    }
  };

  if (isLoading) {
    return (
      <section className={cn("w-full py-12 md:py-24", className)}>
        <div className="container mx-auto px-6">
          <div className="mx-auto mb-12 max-w-3xl text-center">
            <Skeleton className="h-12 w-64 mx-auto mb-4" />
            <Skeleton className="h-6 w-96 mx-auto" />
          </div>
          <div className="grid gap-6 lg:grid-cols-3 mx-auto">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-96 w-full max-w-md mx-auto" />
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (!memberships || memberships.length === 0) {
    return (
      <section className={cn("w-full py-12 md:py-24", className)}>
        <div className="container mx-auto px-6">
          <div className="mx-auto mb-12 max-w-3xl text-center">
            <h2 className="text-4xl md:text-5xl font-semibold leading-tight tracking-tight">
              {heading}
            </h2>
            <p className="mt-2 text-lg text-muted-foreground">
              No membership plans are currently available. Please check back later.
            </p>
          </div>
        </div>
      </section>
    );
  }

  // Filter only available memberships
  const availableMemberships = memberships.filter((m) => m.is_available);
  
  // Mark the middle one as popular if we have 3 or more
  const popularIndex = availableMemberships.length >= 3 
    ? Math.floor(availableMemberships.length / 2) 
    : -1;

  return (
    <section className={cn("w-full py-12 md:py-24", className)}>
      <div className="container mx-auto px-6">
        <div className="mx-auto mb-12 max-w-3xl text-center">
          <h2 className="text-4xl md:text-5xl font-semibold leading-tight tracking-tight">
            {heading}
          </h2>
          <p className="mt-2 text-lg text-muted-foreground">{description}</p>
        </div>
        <div className="grid gap-6 lg:grid-cols-3 mx-auto">
          {availableMemberships.map((membership, index) => {
            const isPopular = index === popularIndex;
            return (
              <div key={membership.id} className="relative">
                {isPopular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10">
                    <Badge>Most Popular</Badge>
                  </div>
                )}
                <Card className={cn(
                  "flex h-full flex-col max-w-md mx-auto gap-4",
                  isPopular && "border-primary border-2"
                )}>
                  <CardHeader>
                    <CardTitle className="mt-4 text-3xl">{membership.name}</CardTitle>
                    <div className="mt-2 flex items-baseline gap-1">
                      <span className="text-4xl font-semibold">
                        {membership.price.toLocaleString()}
                      </span>
                      <span className="text-muted-foreground">RWF/year</span>
                    </div>
                  </CardHeader>
                  <div className="px-4 my-2">
                    <Separator />
                  </div>
                  <CardContent className="flex-1">
                    <p className="text-sm text-muted-foreground mb-4">{membership.description}</p>
                    <ul className="space-y-3">
                      <li className="flex items-center gap-2">
                        <CircleCheck className="size-4 shrink-0 text-primary" />
                        <span>Max order: {membership.max_order_price.toLocaleString()} RWF</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CircleCheck className="size-4 shrink-0 text-primary" />
                        <span>Duration: {membership.duration_days} days</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CircleCheck className="size-4 shrink-0 text-primary" />
                        <span>Annual membership</span>
                      </li>
                    </ul>
                  </CardContent>
                  <CardFooter>
                    <Button
                      className="w-full"
                      variant={isPopular ? "default" : "outline"}
                      size="lg"
                      onClick={() => handleGetStarted(membership.id)}
                    >
                      {isAuthenticated ? "View Details" : "Get Started"}
                    </Button>
                  </CardFooter>
                </Card>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export { Pricing };
