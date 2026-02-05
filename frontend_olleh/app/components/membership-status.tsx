"use client";

import { useQuery } from '@tanstack/react-query';
import { useAuth } from '~/lib/auth-context';
import { membershipApi } from '~/lib/membership';
import type { Membership, UserMembershipDetail, UserMembershipList } from '~/lib/schemas/membership';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Badge } from '~/components/ui/badge';
import { Separator } from '~/components/ui/separator';
import { Skeleton } from '~/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '~/components/ui/alert';
import { CircleCheck, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';
import { format } from 'date-fns';
import { useNavigate } from 'react-router';

/**
 * Component to display active membership
 */
function ActiveMembershipCard({ membership }: { membership: UserMembershipDetail }) {
  const endDate = membership.end_date ? new Date(membership.end_date) : null;
  const startDate = membership.start_date ? new Date(membership.start_date) : null;

  return (
    <Card className="border-primary border-2">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-2xl">Active Membership</CardTitle>
          <Badge variant="default" className="bg-green-600">
            <CircleCheck className="mr-1 h-3 w-3" />
            Active
          </Badge>
        </div>
        <CardDescription>
          You have an active {membership.membership_details.name} membership
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Membership Plan</p>
            <p className="text-lg font-semibold">{membership.membership_details.name}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Price</p>
            <p className="text-lg font-semibold">{membership.membership_details.price.toLocaleString()} RWF</p>
          </div>
          {startDate && (
            <div>
              <p className="text-sm text-muted-foreground">Start Date</p>
              <p className="text-lg font-semibold">{format(startDate, 'MMM dd, yyyy')}</p>
            </div>
          )}
          {endDate && (
            <div>
              <p className="text-sm text-muted-foreground">Expires</p>
              <p className="text-lg font-semibold">{format(endDate, 'MMM dd, yyyy')}</p>
            </div>
          )}
        </div>
        <Separator />
        <div>
          <p className="text-sm text-muted-foreground mb-2">Benefits</p>
          <ul className="space-y-1">
            <li className="flex items-center gap-2 text-sm">
              <CircleCheck className="h-4 w-4 text-primary" />
              Max order price: {membership.membership_details.max_order_price.toLocaleString()} RWF
            </li>
            <li className="flex items-center gap-2 text-sm">
              <CircleCheck className="h-4 w-4 text-primary" />
              Duration: {membership.membership_details.duration_days} days
            </li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Component to display pending membership
 */
function PendingMembershipCard({ membership }: { membership: UserMembershipList }) {
  return (
    <Card className="border-yellow-500 border-2">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-2xl">Pending Membership Request</CardTitle>
          <Badge variant="outline" className="border-yellow-500 text-yellow-700">
            <Clock className="mr-1 h-3 w-3" />
            Pending
          </Badge>
        </div>
        <CardDescription>
          Your request for {membership.membership_name} is pending payment confirmation
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Requested Plan</p>
            <p className="text-lg font-semibold">{membership.membership_name}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Price</p>
            <p className="text-lg font-semibold">{membership.membership_price.toLocaleString()} RWF</p>
          </div>
        </div>
        {membership.payment_mode && (
          <div>
            <p className="text-sm text-muted-foreground">Payment Method</p>
            <p className="text-lg font-semibold capitalize">{membership.payment_mode.replace('_', ' ')}</p>
          </div>
        )}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Payment Pending</AlertTitle>
          <AlertDescription>
            Please complete your payment to activate your membership. Once payment is confirmed, your membership will be activated.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
}

/**
 * Component to display paid membership (awaiting activation)
 */
function PaidMembershipCard({ membership }: { membership: UserMembershipList }) {
  return (
    <Card className="border-blue-500 border-2">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-2xl">Payment Confirmed</CardTitle>
          <Badge variant="outline" className="border-blue-500 text-blue-700">
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Paid
          </Badge>
        </div>
        <CardDescription>
          Your payment for {membership.membership_name} has been confirmed. Your membership will be activated soon.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Membership Plan</p>
            <p className="text-lg font-semibold">{membership.membership_name}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Price</p>
            <p className="text-lg font-semibold">{membership.membership_price.toLocaleString()} RWF</p>
          </div>
        </div>
        {membership.payment_mode && (
          <div>
            <p className="text-sm text-muted-foreground">Payment Method</p>
            <p className="text-lg font-semibold capitalize">{membership.payment_mode.replace('_', ' ')}</p>
          </div>
        )}
        {membership.payment_reference && (
          <div>
            <p className="text-sm text-muted-foreground">Payment Reference</p>
            <p className="text-lg font-semibold">{membership.payment_reference}</p>
          </div>
        )}
        <Alert>
          <CheckCircle2 className="h-4 w-4" />
          <AlertTitle>Awaiting Activation</AlertTitle>
          <AlertDescription>
            Your payment has been confirmed. Your membership will be activated shortly.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
}

/**
 * Component to display available packages and allow selection
 */
function AvailablePackages({ memberships }: { memberships: Membership[] }) {
  const navigate = useNavigate();

  const handleRequestMembership = (membershipId: number) => {
    navigate(`/memberships/request/${membershipId}`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-semibold mb-2">Choose Your Membership</h2>
        <p className="text-muted-foreground">
          Select an annual membership plan to get started with OLLEH
        </p>
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {memberships
          .filter((m) => m.is_available)
          .map((membership) => (
            <Card key={membership.id} className="flex flex-col">
              <CardHeader>
                <CardTitle className="text-2xl">{membership.name}</CardTitle>
                <div className="mt-2">
                  <span className="text-4xl font-semibold">
                    {membership.price.toLocaleString()}
                  </span>
                  <span className="text-muted-foreground ml-2">RWF/year</span>
                </div>
              </CardHeader>
              <CardContent className="flex-1 space-y-4">
                <p className="text-sm text-muted-foreground">{membership.description}</p>
                <Separator />
                <ul className="space-y-2">
                  <li className="flex items-center gap-2 text-sm">
                    <CircleCheck className="h-4 w-4 text-primary" />
                    Max order: {membership.max_order_price.toLocaleString()} RWF
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <CircleCheck className="h-4 w-4 text-primary" />
                    Duration: {membership.duration_days} days
                  </li>
                </ul>
              </CardContent>
              <CardFooter>
                <Button
                  className="w-full"
                  onClick={() => handleRequestMembership(membership.id)}
                >
                  Request Membership
                </Button>
              </CardFooter>
            </Card>
          ))}
      </div>
    </div>
  );
}

/**
 * Main Membership Status Component
 */
export function MembershipStatus() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  // Fetch active membership
  const { data: activeMembership, isLoading: activeLoading } = useQuery({
    queryKey: ['memberships', 'active'],
    queryFn: membershipApi.getActiveMembership,
    enabled: isAuthenticated,
    retry: false,
  });

  // Fetch pending memberships
  const { data: pendingMemberships, isLoading: pendingLoading } = useQuery({
    queryKey: ['memberships', 'pending'],
    queryFn: membershipApi.getPendingMemberships,
    enabled: isAuthenticated,
    retry: false,
  });

  // Fetch all user memberships to check for paid status
  const { data: allMemberships, isLoading: allMembershipsLoading } = useQuery({
    queryKey: ['memberships', 'all'],
    queryFn: membershipApi.getUserMemberships,
    enabled: isAuthenticated && !activeMembership && (!pendingMemberships || pendingMemberships.length === 0),
    retry: false,
  });

  // Find paid memberships (status is 'paid' but not yet active)
  const paidMembership = allMemberships?.find(
    (m) => m.status === 'paid' && !m.is_active
  );

  // Fetch available memberships (only if no active, pending, or paid)
  const { data: availableMemberships, isLoading: availableLoading } = useQuery({
    queryKey: ['memberships', 'available'],
    queryFn: membershipApi.getAvailableMemberships,
    enabled: isAuthenticated && !activeMembership && (!pendingMemberships || pendingMemberships.length === 0) && !paidMembership,
  });

  if (authLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Authentication Required</AlertTitle>
        <AlertDescription>
          Please log in to view and manage your membership.
        </AlertDescription>
      </Alert>
    );
  }

  // Show active membership if exists
  if (activeMembership) {
    if (activeLoading) {
      return <Skeleton className="h-64 w-full" />;
    }
    return <ActiveMembershipCard membership={activeMembership} />;
  }

  // Show pending membership if exists
  if (pendingMemberships && pendingMemberships.length > 0) {
    if (pendingLoading) {
      return <Skeleton className="h-64 w-full" />;
    }
    return <PendingMembershipCard membership={pendingMemberships[0]} />;
  }

  // Show paid membership if exists (awaiting activation)
  if (paidMembership) {
    if (allMembershipsLoading) {
      return <Skeleton className="h-64 w-full" />;
    }
    return <PaidMembershipCard membership={paidMembership} />;
  }

  // Show available packages
  if (availableLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!availableMemberships || availableMemberships.length === 0) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>No Memberships Available</AlertTitle>
        <AlertDescription>
          There are currently no membership plans available. Please check back later.
        </AlertDescription>
      </Alert>
    );
  }

  return <AvailablePackages memberships={availableMemberships} />;
}
