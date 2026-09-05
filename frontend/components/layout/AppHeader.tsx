"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth, useLogout } from "@/lib/hooks/use-auth";

interface AppHeaderProps {
  onOpenMobileMenu: () => void;
}

export function AppHeader({ onOpenMobileMenu }: AppHeaderProps) {
  const router = useRouter();
  const { user } = useAuth();
  const logoutMutation = useLogout();

  const handleSignOut = () => {
    logoutMutation.mutate(undefined, {
      onSuccess: () => {
        router.push("/login");
      },
    });
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-[#E8D8BD] bg-[#FFFDF5] px-4 md:px-6">
      {/* Mobile Toggle & Portal Identifier */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenMobileMenu}
          className="inline-flex items-center justify-center border border-[#E8D8BD] bg-[#FFF8E7] p-2 text-[#3B2921] hover:bg-[#F3EFE6] md:hidden"
          style={{ borderRadius: "3px" }}
          aria-label="Open navigation sidebar"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span className="hidden text-xs font-semibold uppercase tracking-wider text-[#6B5A4A] sm:inline">
          Academic Management Desk
        </span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        <Link
          href="/"
          target="_blank"
          className="hidden border border-[#E8D8BD] bg-[#FFF8E7] px-2.5 py-1 text-xs font-medium text-[#6B5A4A] hover:border-[#D96B27] hover:text-[#D96B27] sm:inline-flex"
          style={{ borderRadius: "3px" }}
        >
          Public Portal ↗
        </Link>

        {/* User Identity Capsule */}
        <div className="flex items-center gap-2 border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-1.5" style={{ borderRadius: "3px" }}>
          <div className="flex h-6 w-6 items-center justify-center bg-[#D96B27] text-xs font-bold text-white" style={{ borderRadius: "2px" }}>
            {user?.name ? user.name.charAt(0).toUpperCase() : user?.email ? user.email.charAt(0).toUpperCase() : "U"}
          </div>
          <div className="flex flex-col text-left">
            <span className="text-xs font-bold text-[#3B2921]">{user?.name ?? user?.email ?? "Authenticated User"}</span>
            <span className="text-[10px] uppercase tracking-wider text-[#6B5A4A]">{user?.role ?? "User"}</span>
          </div>
        </div>

        {/* Sign Out Action */}
        <button
          type="button"
          onClick={handleSignOut}
          disabled={logoutMutation.isPending}
          className="border border-[#B94E27] bg-[#FFF8E7] px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-[#B94E27] transition hover:bg-[#B94E27] hover:text-white disabled:opacity-50"
          style={{ borderRadius: "3px" }}
        >
          {logoutMutation.isPending ? "Signing Out..." : "Sign Out"}
        </button>
      </div>
    </header>
  );
}