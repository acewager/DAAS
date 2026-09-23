import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { Link, useLocation } from "react-router-dom";
import { confirmPasswordReset, requestPasswordReset } from "@/services/authService";

export default function PasswordResetPage() {
  const query = new URLSearchParams(useLocation().search); const uid = query.get("uid"); const token = query.get("token");
  const request = useMutation({ mutationFn: requestPasswordReset }); const confirm = useMutation({ mutationFn: confirmPasswordReset });
  const form = useForm<{ email: string; password: string; confirmPassword: string }>({}); const isConfirm = Boolean(uid && token);
  return <div className="mx-auto flex min-h-[70vh] max-w-md items-center px-4"><div className="w-full rounded-2xl border bg-white p-6 shadow-sm"><h1 className="text-2xl font-semibold">{isConfirm ? "Choose a new password" : "Reset password"}</h1><form className="mt-5 space-y-4" onSubmit={form.handleSubmit((v) => isConfirm ? confirm.mutate({ uid: uid!, token: token!, password: v.password, confirmPassword: v.confirmPassword }) : request.mutate(v.email))}>{isConfirm ? <><input type="password" placeholder="New password" className="w-full rounded border p-2" {...form.register("password", { required: true })}/><input type="password" placeholder="Confirm password" className="w-full rounded border p-2" {...form.register("confirmPassword", { required: true })}/></> : <input type="email" placeholder="Email" className="w-full rounded border p-2" {...form.register("email", { required: true })}/>}<button className="rounded bg-blue-600 px-4 py-2 text-white">{isConfirm ? "Reset password" : "Send reset link"}</button></form>{(request.isSuccess || confirm.isSuccess) && <p className="mt-3 text-sm text-green-700">{isConfirm ? "Password reset. You can now sign in." : "If that email is registered, a reset link has been sent."}</p>}<Link className="mt-4 block text-sm text-blue-600" to="/login">Back to sign in</Link></div></div>;
}
