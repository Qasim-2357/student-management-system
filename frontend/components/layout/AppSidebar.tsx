"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BrandMark } from "@/components/site/BrandMark";
import { useAuth } from "@/lib/hooks/use-auth";
import { Award } from "lucide-react";
import type { ComponentType } from "react";

interface NavItem {
  label: string;
  href: string;
  roles: ("ADMIN" | "TEACHER" | "STUDENT")[];
  icon: ComponentType<{ className?: string }>;
}

function GridIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
    </svg>
  );
}

function UsersIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
    </svg>
  );
}

function AcademicCapIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
    </svg>
  );
}

function BuildingIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21" />
    </svg>
  );
}

function BookIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
    </svg>
  );
}

function DocumentCheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125v-12m-9.375-6.375l6.375 6.375m-6.375-6.375v4.875c0 .621.504 1.125 1.125 1.125h4.875M9 14.25l2.25 2.25 4.5-4.5" />
    </svg>
  );
}

function CalendarIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
    </svg>
  );
}

function ChartBarIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  );
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", roles: ["ADMIN", "TEACHER", "STUDENT"], icon: GridIcon },
  { label: "Students", href: "/students", roles: ["ADMIN", "TEACHER"], icon: UsersIcon },
  { label: "Teachers", href: "/teachers", roles: ["ADMIN"], icon: AcademicCapIcon },
  { label: "Classes", href: "/classes", roles: ["ADMIN", "TEACHER"], icon: BuildingIcon },
  { label: "Subjects", href: "/subjects", roles: ["ADMIN"], icon: BookIcon },
  { label: "Examinations", href: "/exams", roles: ["ADMIN", "TEACHER"], icon: DocumentCheckIcon },
  { label: "Attendance", href: "/attendance", roles: ["ADMIN", "TEACHER"], icon: CalendarIcon },
  { label: "Marks", href: "/marks", roles: ["ADMIN", "TEACHER"], icon: ChartBarIcon },
  {
    label: "Performance",
    href: "/performance",
    icon: Award,
    roles: ["ADMIN", "TEACHER", "STUDENT"],
  },
];

export function AppSidebar({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname();
  const { user } = useAuth();
  const role: NavItem["roles"][number] = user?.role
    ? (user.role.toUpperCase() as NavItem["roles"][number])
    : "ADMIN";

  const allowedItems = NAV_ITEMS.filter((item) => item.roles.includes(role));

  return (
    <aside className="flex h-full w-64 flex-col border-r border-[#E8D8BD] bg-[#FFF8E7] text-[#3B2921]">
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between border-b border-[#E8D8BD] px-4">
        <Link href="/dashboard" onClick={onClose} className="inline-flex items-center">
          <BrandMark size="sm" />
        </Link>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-[#6B5A4A] hover:bg-[#F3EFE6] hover:text-[#3B2921] md:hidden"
            aria-label="Close sidebar"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Role Banner */}
      <div className="border-b border-[#E8D8BD] bg-[#FFFDF5] px-4 py-2.5 text-xs">
        <span className="text-[10px] font-bold uppercase tracking-wider text-[#6B5A4A]">Active Desk</span>
        <div className="flex items-center gap-1.5 font-semibold text-[#D96B27]">
          <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
          {role === "ADMIN" ? "Administrator" : role === "TEACHER" ? "Faculty Desk" : "Student Desk"}
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-2 py-3" aria-label="Portal Navigation">
        {allowedItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={`group flex items-center gap-3 px-3 py-2 text-xs font-semibold uppercase tracking-wider transition ${
                isActive
                  ? "border border-[#B94E27] bg-[#D96B27] text-white"
                  : "text-[#3B2921] hover:border hover:border-[#E8D8BD] hover:bg-[#FFFDF5] hover:text-[#D96B27]"
              }`}
              style={{ borderRadius: "3px" }}
            >
              <Icon className={`h-4 w-4 ${isActive ? "text-white" : "text-[#6B5A4A] group-hover:text-[#D96B27]"}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Institutional Footer Info */}
      <div className="border-t border-[#E8D8BD] bg-[#FFFDF5] p-3 text-xs text-[#6B5A4A]">
        <div className="font-semibold text-[#3B2921]">Session 2026–2027</div>
        <p className="mt-0.5 text-[11px]">Central Academic Registry</p>
      </div>
    </aside>
  );
}
