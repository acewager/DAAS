import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { useAuth } from "@/contexts/AuthContext";
import { loginAccount } from "@/services/authService";

const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const loginMutation = useMutation({
    mutationFn: loginAccount,
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
          <h1 className="text-2xl font-semibold">Sign in</h1>
          <p className="text-sm text-slate-500">Use your account to manage desktop instances.</p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit((values) => loginMutation.mutate(values))}>
          <div>
            <label className="mb-1 block text-sm font-medium" htmlFor="username">Username</label>
            <input id="username" className="w-full rounded-lg border border-border bg-transparent px-3 py-2 outline-none focus:border-blue-600" {...register("username")} />
            {errors.username && <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium" htmlFor="password">Password</label>
            <input id="password" type="password" className="w-full rounded-lg border border-border bg-transparent px-3 py-2 outline-none focus:border-blue-600" {...register("password")} />
            {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}
          </div>

          {loginMutation.isError && (
            <p className="text-sm text-red-600">Unable to sign in. Check your credentials and try again.</p>
          )}

          <button className="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white disabled:opacity-60" disabled={loginMutation.isPending} type="submit">
            {loginMutation.isPending ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="mt-4 text-sm text-slate-500">
          Need an account? <Link to="/register" className="font-medium text-blue-600">Register</Link>
        </p>
        <p className="mt-2 text-sm text-slate-500">
          <Link to="/reset-password" className="font-medium text-blue-600">Forgot your password?</Link>
        </p>
      </div>
    </div>
  );
}
