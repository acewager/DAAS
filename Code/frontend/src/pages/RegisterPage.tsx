import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { useAuth } from "@/contexts/AuthContext";
import { registerAccount } from "@/services/authService";

const registerSchema = z.object({
  username: z.string().min(1, "Username is required"),
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(8, "Use at least 8 characters"),
  confirmPassword: z.string().min(1, "Confirm your password"),
}).refine((values) => values.password === values.confirmPassword, {
  path: ["confirmPassword"],
  message: "Passwords do not match",
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const registerMutation = useMutation({
    mutationFn: registerAccount,
    onSuccess: async (user) => {
      setUser(user);
      navigate("/", { replace: true });
    },
  });

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md items-center px-4">
      <div className="w-full rounded-2xl border border-border bg-white p-6 shadow-sm dark:bg-slate-900">
        <div className="mb-6 space-y-2">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-blue-600">Desktop Cloud Platform</p>
          <h1 className="text-2xl font-semibold">Create account</h1>
          <p className="text-sm text-slate-500">Register to provision and manage desktop instances.</p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit((values) => registerMutation.mutate(values))}>
          <div>
            <label className="mb-1 block text-sm font-medium" htmlFor="username">Username</label>
            <input id="username" className="w-full rounded-lg border border-border bg-transparent px-3 py-2 outline-none focus:border-blue-600" {...register("username")} />
            {errors.username && <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium" htmlFor="email">Email</label>
            <input id="email" type="email" className="w-full rounded-lg border border-border bg-transparent px-3 py-2 outline-none focus:border-blue-600" {...register("email")} />
            {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium" htmlFor="password">Password</label>
            <input id="password" type="password" className="w-full rounded-lg border border-border bg-transparent px-3 py-2 outline-none focus:border-blue-600" {...register("password")} />
            {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium" htmlFor="confirmPassword">Confirm password</label>
            <input id="confirmPassword" type="password" className="w-full rounded-lg border border-border bg-transparent px-3 py-2 outline-none focus:border-blue-600" {...register("confirmPassword")} />
            {errors.confirmPassword && <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>}
          </div>

          {registerMutation.isError && (
            <p className="text-sm text-red-600">Unable to create your account. Check the form and try again.</p>
          )}

          <button className="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white disabled:opacity-60" disabled={registerMutation.isPending} type="submit">
            {registerMutation.isPending ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="mt-4 text-sm text-slate-500">
          Already registered? <Link to="/login" className="font-medium text-blue-600">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
