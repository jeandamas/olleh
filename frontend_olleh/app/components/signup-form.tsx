import { cn } from "~/lib/utils"
import { Button } from "~/components/ui/button"
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldSeparator,
} from "~/components/ui/field"
import { Input } from "~/components/ui/input"
import { Link } from "react-router"

export function SignupForm({
  className,
  ...props
}: React.ComponentProps<"form">) {
  return (
    <form className={cn("flex flex-col gap-6", className)} {...props}>
      <FieldGroup>
        <div className="flex flex-col items-center gap-1 text-center">
          <h1 className="text-2xl font-bold">Sign up for an account</h1>
          <p className="text-muted-foreground text-sm text-balance">
            Enter your email below to sign up for an account
          </p>
        </div>
        <Field>
          <FieldLabel htmlFor="email">Email</FieldLabel>
          <Input id="email" type="email" placeholder="m@example.com" required />
        </Field>
        <Field>
          <div className="flex items-center">
            <FieldLabel htmlFor="password">Password</FieldLabel>
            
          </div>
          <Input id="password" type="password" required />
        </Field>
        <Field>
          <div className="flex items-center">
            <FieldLabel htmlFor="password">Repeat Password</FieldLabel>
            
          </div>
          <Input id="password" type="password" required />
        </Field>
        
        <Field>
          <Button type="submit">Login</Button>
        </Field>
        <FieldSeparator>Already have an account? 
            <Link to="/login" className="underline underline-offset-4">Login
            </Link>
            </FieldSeparator>
        
      </FieldGroup>
    </form>
  )
}
