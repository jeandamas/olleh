import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router';
import { membershipApi } from '~/lib/membership';
import type { Membership } from '~/lib/schemas/membership';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '~/components/ui/alert';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '~/components/ui/select';
import { Input } from '~/components/ui/input';
import { Label } from '~/components/ui/label';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { userMembershipCreateSchema, type UserMembershipCreate } from '~/lib/schemas/membership';
import type { ApiError } from '~/lib/api-client';
import { ProtectedRoute } from '~/components/protected-route';
import { Skeleton } from '~/components/ui/skeleton';

export default function MembershipRequestPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const membershipId = id ? parseInt(id, 10) : null;

  // Fetch membership details
  const { data: membership, isLoading: membershipLoading } = useQuery({
    queryKey: ['membership', membershipId],
    queryFn: () => membershipApi.getMembership(membershipId!),
    enabled: !!membershipId,
  });

  // Form schema without membership (since it comes from URL)
  const membershipRequestFormSchema = userMembershipCreateSchema.omit({ membership: true });

  const {
    register,
    handleSubmit,
    control,
    setError,
    formState: { errors },
  } = useForm<z.infer<typeof membershipRequestFormSchema>>({
    resolver: zodResolver(membershipRequestFormSchema),
    defaultValues: {
      payment_mode: null,
      payment_reference: null,
      amount_paid: null,
    },
  });

  const createMutation = useMutation({
    mutationFn: membershipApi.createMembershipRequest,
    onSuccess: () => {
      toast.success('Membership request created successfully!');
      queryClient.invalidateQueries({ queryKey: ['memberships', 'pending'] });
      queryClient.invalidateQueries({ queryKey: ['memberships', 'active'] });
      navigate(-1); // Go back to previous page
    },
    onError: (error: Error & { data?: ApiError; status?: number }) => {
      // Parse API error response
      const errorData = error.data || {};
      const errorMessages: string[] = [];

      // Set field errors on the form
      Object.keys(errorData).forEach((key) => {
        const fieldValue = errorData[key];
        
        // Skip non-field error keys
        if (key === 'detail' || key === 'message' || key === 'non_field_errors') {
          if (Array.isArray(fieldValue)) {
            errorMessages.push(...fieldValue);
          } else if (fieldValue) {
            errorMessages.push(String(fieldValue));
          }
          return;
        }

        // Set field-specific errors
        if (Array.isArray(fieldValue) && fieldValue.length > 0) {
          const fieldName = key as keyof z.infer<typeof membershipRequestFormSchema>;
          setError(fieldName, {
            type: 'server',
            message: fieldValue[0], // Use first error message
          });
          errorMessages.push(`${fieldValue[0]}`);
        } else if (fieldValue) {
          const fieldName = key as keyof z.infer<typeof membershipRequestFormSchema>;
          setError(fieldName, {
            type: 'server',
            message: String(fieldValue),
          });
          errorMessages.push(String(fieldValue));
        }
      });

      // Show toast with error message(s)
      const toastMessage = errorMessages.length > 0
        ? errorMessages.join('. ')
        : error.message || 'Failed to create membership request';
      
      toast.error(toastMessage);
    },
  });

  const onSubmit = (data: z.infer<typeof membershipRequestFormSchema>) => {
    if (!membershipId) return;

    createMutation.mutate({
      ...data,
      membership: membershipId,
    } as UserMembershipCreate);
  };

  if (!membershipId) {
    return (
      <ProtectedRoute>
        <div className="container mx-auto px-4 py-8 max-w-2xl">
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Invalid Membership</AlertTitle>
            <AlertDescription>
              The membership ID is invalid. Please go back and try again.
            </AlertDescription>
          </Alert>
          <Button onClick={() => navigate(-1)} className="mt-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Back
          </Button>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-6 sm:py-8 max-w-2xl">
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="mb-6"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>

        <Card>
          <CardHeader>
            <CardTitle className="text-2xl sm:text-3xl">Request Membership</CardTitle>
            <CardDescription>
              Complete your membership request by providing payment information (optional - you can update this later)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {membershipLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : membership ? (
              <>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Selected Plan</p>
                  <p className="text-lg sm:text-xl font-semibold mt-1">{membership.name}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {membership.price.toLocaleString()} RWF/year
                  </p>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="payment-mode">How did you pay?</Label>
                    <Controller
                      name="payment_mode"
                      control={control}
                      render={({ field }) => (
                        <Select
                          value={field.value || ''}
                          onValueChange={(value) => field.onChange(value || null)}
                        >
                          <SelectTrigger
                            id="payment-mode"
                            className="w-full"
                            aria-invalid={errors.payment_mode ? 'true' : 'false'}
                          >
                            <SelectValue placeholder="Select payment method" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="mobile_money">Mobile Money</SelectItem>
                            <SelectItem value="cash">Cash</SelectItem>
                            <SelectItem value="bank">Bank Transfer</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    />
                    {errors.payment_mode && (
                      <p className="text-sm text-destructive mt-1">
                        {errors.payment_mode.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="payment-reference">
                      Payment Reference (Optional)
                    </Label>
                    <Input
                      id="payment-reference"
                      placeholder="Transaction ID, receipt number, etc."
                      {...register('payment_reference')}
                      className="w-full"
                      aria-invalid={errors.payment_reference ? 'true' : 'false'}
                    />
                    {errors.payment_reference && (
                      <p className="text-sm text-destructive mt-1">
                        {errors.payment_reference.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="amount-paid">Confirm Amount Paid</Label>
                    <Input
                      id="amount-paid"
                      type="number"
                      placeholder="Amount in RWF"
                      {...register('amount_paid', {
                        valueAsNumber: true,
                        setValueAs: (value) => (value === '' ? null : Number(value)),
                      })}
                      className="w-full"
                      aria-invalid={errors.amount_paid ? 'true' : 'false'}
                    />
                    {errors.amount_paid && (
                      <p className="text-sm text-destructive mt-1">
                        {errors.amount_paid.message}
                      </p>
                    )}
                  </div>

                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Note</AlertTitle>
                  <AlertDescription>
                    Once you paid for membership, you can submit your request.
                  </AlertDescription>
                </Alert>

                  <div className="flex flex-col sm:flex-row gap-3 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => navigate(-1)}
                      className="w-full sm:w-auto"
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      disabled={createMutation.isPending}
                      className="w-full sm:w-auto sm:ml-auto"
                    >
                      {createMutation.isPending ? 'Submitting...' : 'Submit Request'}
                    </Button>
                  </div>
                </form>
              </>
            ) : (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Membership Not Found</AlertTitle>
                <AlertDescription>
                  The membership you're looking for doesn't exist or is no longer available.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      </div>
    </ProtectedRoute>
  );
}
