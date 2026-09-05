"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BrandMark } from "@/components/site/BrandMark";

const NAV_LINKS = [
  { label: "Home", href: "/" },
  { label: "About", href: "/about" },
  { label: "Academics", href: "/academics" },
  { label: "Curriculum", href: "/curriculum" },
  { label: "Faculty", href: "/faculty" },
  { label: "Examinations", href: "/examinations" },
  { label: "Results", href: "/results" },
  { label: "Notices", href: "/notices" },
  { label: "Contact", href: "/contact" },
];

export function PublicHeader() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="w-full bg-[#FFF8E7] text-[#3B2921]">
      {/* 1. Thin Warm Utility Bar (Deep Institutional Brown) */}
      <div className="border-b border-[#5C4235] bg-[#3B2921] text-[#F3E7D0]">
        <div className="mx-auto flex h-8 max-w-7xl items-center justify-between px-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#E8A317]" />
            <span className="font-medium text-[#FFFDF5]">
              Student Management Portal
            </span>
          </div>

          <div className="flex items-center divide-x divide-[#5C4235]">
            <Link
              href="/dashboard"
              className="px-3 text-xs text-[#E8A317] hover:text-[#FFFFFF]"
            >
              Academic Desk
            </Link>
            <Link
              href="/notices"
              className="px-3 text-xs text-[#F3E7D0] hover:text-[#FFFFFF]"
            >
              Notices
            </Link>
            <Link
              href="/contact"
              className="pl-3 text-xs text-[#F3E7D0] hover:text-[#FFFFFF]"
            >
              Contact
            </Link>
          </div>
        </div>
      </div>

      {/* 2. Main Identity Header */}
      <div className="border-b border-[#E8D8BD] bg-[#FFF8E7]">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4">
          <Link href="/" className="inline-flex items-center">
            <BrandMark size="md" />
          </Link>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="inline-flex items-center border border-[#B94E27] bg-[#D96B27] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white transition hover:bg-[#B94E27] focus:outline-none focus:ring-2 focus:ring-[#D96B27] focus:ring-offset-2"
              style={{ borderRadius: "3px" }}
            >
              Portal Login
            </Link>

            {/* Mobile Toggle Button */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              className="inline-flex items-center justify-center border border-[#E8D8BD] bg-[#FFFDF5] p-2 text-[#3B2921] hover:bg-[#F5EAD4] focus:outline-none focus:ring-2 focus:ring-[#D96B27] lg:hidden"
              style={{ borderRadius: "3px" }}
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle Navigation Menu"
            >
              <svg
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {mobileMenuOpen ? (
                  <path
                    strokeLinecap="square"
                    strokeLinejoin="miter"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="square"
                    strokeLinejoin="miter"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* 3. Amber/Orange Primary Navigation Bar (Desktop) */}
      <nav
        aria-label="Primary Navigation"
        className="hidden border-b border-[#B94E27] bg-[#D96B27] text-white lg:block"
      >
        <div className="mx-auto flex max-w-7xl items-stretch px-4">
          {NAV_LINKS.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.label}
                href={item.href}
                className={`relative inline-flex items-center px-4 py-2.5 text-xs font-semibold uppercase tracking-wider transition-colors ${
                  isActive
                    ? "bg-[#B94E27] text-white"
                    : "text-[#FFFDF5] hover:bg-[#C2581F] hover:text-white"
                }`}
              >
                {item.label}
                {isActive && (
                  <span
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#E8A317]"
                    aria-hidden="true"
                  />
                )}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="border-b border-[#B94E27] bg-[#D96B27] text-white lg:hidden">
          <div className="divide-y divide-[#C2581F] px-4 py-2">
            {NAV_LINKS.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);

              return (
                <Link
                  key={item.label}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block py-2.5 text-xs font-semibold uppercase tracking-wider ${
                    isActive
                      ? "text-[#E8A317]"
                      : "text-white hover:text-[#FFFDF5]"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </header>
  );
}