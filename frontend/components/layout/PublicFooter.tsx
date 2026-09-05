import React from "react";
import Link from "next/link";
import { BrandMark } from "@/components/site/BrandMark";

export function PublicFooter() {
  return (
    <footer className="border-t border-[#E8D8BD] bg-[#FFFDF5] text-[#3B2921]">
      {/* Upper Footer Grid (Warm Ivory/White Surface Background) */}
      <div className="mx-auto max-w-7xl px-4 py-10 sm:py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-5">
          {/* Col 1 & 2: Institutional Brand & Mission */}
          <div className="space-y-3 lg:col-span-2">
            {/* Logo scaled ~15-20% larger while preserving artwork & alignment */}
            <div className="origin-left scale-115 transform-gpu">
              <BrandMark size="md" />
            </div>
            <p className="max-w-md text-xs leading-relaxed text-[#6B5A4A]">
              Student Sphere coordinates student records, evaluation metrics, curriculum delivery, and institutional circulars. An academic operating system designed for modern collegiate governance.
            </p>
            <div className="pt-2 text-xs font-medium text-[#6B5A4A]">
              <span className="block text-[#3B2921] font-semibold">Central Administrative Registry</span>
              Session Academic Year 2026–2027
            </div>
          </div>

          {/* Col 3: Academic Operations */}
          <div className="space-y-3">
            <h4 className="font-serif text-xs font-bold uppercase tracking-wider text-[#3B2921]">
              Academics
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/academics" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Academic Divisions
                </Link>
              </li>
              <li>
                <Link href="/curriculum" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Curricular Syllabi
                </Link>
              </li>
              <li>
                <Link href="/examinations" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Examination Schemes
                </Link>
              </li>
              <li>
                <Link href="/results" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Evaluation &amp; Results
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 4: Institutional Services */}
          <div className="space-y-3">
            <h4 className="font-serif text-xs font-bold uppercase tracking-wider text-[#3B2921]">
              Institutional
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/about" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Institutional Charter
                </Link>
              </li>
              <li>
                <Link href="/faculty" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Faculty Directory
                </Link>
              </li>
              <li>
                <Link href="/notices" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Circulars &amp; Notices
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Office Directory
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 5: Student Desks */}
          <div className="space-y-3">
            <h4 className="font-serif text-xs font-bold uppercase tracking-wider text-[#3B2921]">
              Student Access
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/login" className="text-[#D96B27] font-semibold hover:underline">
                  Portal Login &rarr;
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Academic Desk
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-[#6B5A4A] hover:text-[#D96B27]">
                  Helpdesk &amp; Inquiries
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Sub-Footer Strip (Institutional Dark Brown #3B2921) */}
      <div className="border-t border-[#5C4235] bg-[#3B2921] text-[#E5D8BD]">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-4 py-4 text-xs sm:flex-row">
          <p className="text-[#F3E7D0]">© 2026 Student Sphere Academic Portal. All institutional rights reserved.</p>
          <div className="flex items-center space-x-4 text-xs font-medium">
            <Link href="/about" className="text-[#F3E7D0] hover:text-[#E8A317]">Governance Regulations</Link>
            <span className="text-[#6B5A4A]">•</span>
            <Link href="/notices" className="text-[#F3E7D0] hover:text-[#E8A317]">Public Dispatches</Link>
            <span className="text-[#6B5A4A]">•</span>
            <Link href="/contact" className="text-[#F3E7D0] hover:text-[#E8A317]">Registrar Support</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}