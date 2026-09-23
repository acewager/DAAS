import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { useAuth } from "@/contexts/AuthContext";
import { updateProfile } from "@/services/authService";

export default function ProfilePage() {
  const { user, setUser } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues: { username: user?.username ?? "", email: user?.email ?? "" } });
  const mutation = useMutation({ mutationFn: updateProfile, onSuccess: setUser });
  return <div className="max-w-md space-y-4"><h1 className="text-2xl font-semibold">Profile</h1><form className="space-y-4" onSubmit={handleSubmit((values) => mutation.mutate(values))}><label className="block text-sm">Username<input className="mt-1 w-full rounded border p-2" {...register("username", { required: "Username is required" })} /></label><label className="block text-sm">Email<input type="email" className="mt-1 w-full rounded border p-2" {...register("email", { required: "Email is required" })} /></label>{(errors.username || errors.email || mutation.isError) && <p className="text-sm text-red-600">Unable to update profile.</p>}<button className="rounded bg-blue-600 px-4 py-2 text-white" disabled={mutation.isPending}>Save changes</button>{mutation.isSuccess && <p className="text-sm text-green-700">Profile updated.</p>}</form></div>;
}
