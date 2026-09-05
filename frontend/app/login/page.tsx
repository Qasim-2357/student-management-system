"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { BrandMark } from "@/components/site/BrandMark";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useLogin } from "@/lib/hooks/use-auth";
import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const loginSchema = z.object({
  username: z.string().min(1, "Identifier is required"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

type DemoRole = "ADMIN" | "TEACHER" | "STUDENT";

const DEMO_CREDENTIALS: Record<DemoRole, { username: string; label: string; desc: string }> = {
  ADMIN: {
    username: "admin@example.com",
    label: "Administrator",
    desc: "Institutional Governance & Master Registry",
  },
  TEACHER: {
    username: "teacher",
    label: "Faculty Desk",
    desc: "Attendance Rosters, Syllabus & Mark Entry",
  },
  STUDENT: {
    username: "student",
    label: "Student Desk",
    desc: "Enrollment Record, Marks & Circulars",
  },
};

export default function LoginPage() {
  const loginMutation = useLogin();
  const [error, setError] = useState<string | null>(null);
  const [selectedRole, setSelectedRole] = useState<DemoRole>("ADMIN");

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: DEMO_CREDENTIALS.ADMIN.username,
      password: "",
    },
  });

  const handleRoleSelect = (role: DemoRole) => {
    setSelectedRole(role);
    setValue("username", DEMO_CREDENTIALS[role].username);
    setValue("password", "");
    setError(null);
  };

  const onSubmit = (data: LoginFormValues) => {
    setError(null);
    loginMutation.mutate(
      {
        email: data.username,
        password: data.password,
      },
      {
        onError: (err: Error) => {
          setError(err.message || "Invalid credentials. Please verify username and password.");
        },
      }
    );
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex flex-1 items-center justify-center px-4 py-12">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center">
            <Link href="/" className="inline-flex justify-center">
              <BrandMark size="lg" />
            </Link>
            <h1 className="mt-3 font-serif text-xl font-bold tracking-tight text-[#3B2921]">
              Institutional Portal Login
            </h1>
            <p className="text-xs text-[#6B5A4A]">
              Central authentication gateway for students, faculty, and administrative staff.
            </p>
          </div>

          <Card
            className="border-[#E8D8BD] bg-[#FFFDF5] text-[#3B2921] shadow-xs"
            style={{ borderRadius: "4px" }}
          >
            <CardHeader className="border-b border-[#E8D8BD] pb-4">
              <CardTitle className="font-serif text-base font-bold text-[#3B2921]">
                Sign In to Academic Account
              </CardTitle>
              <CardDescription className="text-xs text-[#6B5A4A]">
                Select your designated role to load corresponding account identifier.
              </CardDescription>

              <div className="mt-3 grid grid-cols-3 gap-1 border border-[#E8D8BD] bg-[#FFF8E7] p-1 text-center" style={{ borderRadius: "3px" }}>
                {(Object.keys(DEMO_CREDENTIALS) as DemoRole[]).map((role) => {
                  const isSelected = selectedRole === role;
                  return (
                    <button
                      key={role}
                      type="button"
                      onClick={() => handleRoleSelect(role)}
                      className={`py-1.5 text-[11px] font-semibold uppercase tracking-wider transition ${
                        isSelected
                          ? "bg-[#D96B27] text-white"
                          : "text-[#6B5A4A] hover:bg-[#F5EAD4] hover:text-[#3B2921]"
                      }`}
                      style={{ borderRadius: "2px" }}
                    >
                      {DEMO_CREDENTIALS[role].label}
                    </button>
                  );
                })}
              </div>
            </CardHeader>

            <CardContent className="pt-6">
              {error && (
                <Alert
                  variant="destructive"
                  className="mb-4 border-[#B94E27] bg-[#FFF8E7] text-[#B94E27]"
                  style={{ borderRadius: "3px" }}
                >
                  <AlertDescription className="text-xs font-medium">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="username" className="text-xs font-semibold text-[#3B2921]">
                    Institutional Username / Identifier
                  </Label>
                  <Input
                    id="username"
                    type="text"
                    autoComplete="username"
                    className="border-[#E8D8BD] bg-[#FFFDF5] text-xs text-[#3B2921] focus:border-[#D96B27] focus:ring-[#D96B27]"
                    style={{ borderRadius: "3px" }}
                    {...register("username")}
                  />
                  {errors.username && (
                    <p className="text-[11px] text-[#B94E27]">{errors.username.message}</p>
                  )}
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="password" className="text-xs font-semibold text-[#3B2921]">
                    Account Security Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    autoComplete="current-password"
                    className="border-[#E8D8BD] bg-[#FFFDF5] text-xs text-[#3B2921] focus:border-[#D96B27] focus:ring-[#D96B27]"
                    style={{ borderRadius: "3px" }}
                    {...register("password")}
                  />
                  {errors.password && (
                    <p className="text-[11px] text-[#B94E27]">{errors.password.message}</p>
                  )}
                </div>

                <Button
                  type="submit"
                  disabled={loginMutation.isPending}
                  className="w-full border border-[#B94E27] bg-[#D96B27] py-2 text-xs font-semibold uppercase tracking-wider text-white hover:bg-[#B94E27] disabled:opacity-50"
                  style={{ borderRadius: "3px" }}
                >
                  {loginMutation.isPending ? "Authenticating Session..." : "Authorize Portal Login"}
                </Button>
              </form>

              <div className="mt-4 border-t border-[#E8D8BD] pt-3 text-center text-[11px] text-[#6B5A4A]">
                <p>Protected by Student Sphere Role-Gated Access Control</p>
                <p className="mt-1">
                  Need credential recovery?{" "}
                  <Link href="/contact" className="font-semibold text-[#D96B27] hover:underline">
                    Inquire at Registry Desk
                  </Link>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
}