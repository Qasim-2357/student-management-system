"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useClasses } from "@/lib/hooks/use-classes";
import type { Student, StudentCreate } from "@/lib/types/students";
import Link from "next/link";

const studentSchema = z.object({
  first_name: z.string().min(1, "First name is required").max(50),
  last_name: z.string().min(1, "Last name is required").max(50),
  roll_number: z.string().min(1, "Roll number is required").max(30),
  email: z.string().email("Valid institutional email required"),
  phone: z.string().min(1, "Phone is required").max(20),
  course: z.string().min(1, "Course is required").max(100),
  semester: z.number().int().positive("Semester must be positive"),
  academic_class_id: z.string().optional(),
});

type StudentFormValues = z.infer<typeof studentSchema>;

export interface StudentFormProps {
  initialData?: Student;
  onSubmit: (data: StudentCreate) => Promise<void>;
  busy?: boolean;
  submitLabel?: string;
}

export function StudentForm({ initialData, onSubmit, busy = false, submitLabel = "Save Student" }: StudentFormProps) {
  const { data: classesResponse } = useClasses({});

  const classList = (() => {
    if (!classesResponse) return [];
    if (Array.isArray(classesResponse)) return classesResponse;
    const res = classesResponse as unknown as { items?: Array<{ id: number; name: string; academic_year?: string }>; data?: Array<{ id: number; name: string; academic_year?: string }> };
    return res.items ?? res.data ?? [];
  })();

  const studentObj = (initialData ?? {}) as unknown as Record<string, unknown>;

  const defaultFirstName =
    typeof studentObj.first_name === "string"
      ? studentObj.first_name
      : typeof studentObj.name === "string"
      ? studentObj.name.split(" ")[0]
      : "";

  const defaultLastName =
    typeof studentObj.last_name === "string"
      ? studentObj.last_name
      : typeof studentObj.name === "string"
      ? studentObj.name.split(" ").slice(1).join(" ")
      : "";

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<StudentFormValues>({
    resolver: zodResolver(studentSchema),
    defaultValues: {
      first_name: defaultFirstName,
      last_name: defaultLastName,
      roll_number: initialData?.roll_number ?? "",
      email: initialData?.email ?? "",
      phone: initialData?.phone ?? "",
      course: initialData?.course ?? "",
      semester: initialData?.semester ?? 1,
      academic_class_id: initialData?.academic_class_id ? String(initialData.academic_class_id) : "",
    },
  });

  const onFormSubmit = async (values: StudentFormValues) => {
    const fullName = `${values.first_name.trim()} ${values.last_name.trim()}`.trim();
    
    // Construct payload compatible with StudentCreate ({ name, roll_number, email, ... })
    const payload: StudentCreate = {
      name: fullName,
      roll_number: values.roll_number,
      email: values.email,
      phone: values.phone,
      course: values.course,
      semester: values.semester,
      academic_class_id: values.academic_class_id ? Number(values.academic_class_id) : undefined,
    };

    await onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      <div className="space-y-4">
        <h2 className="border-b border-[#E8D8BD] pb-3 font-serif text-base font-bold text-[#3B2921]">
          Demographic &amp; Registration Information
        </h2>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {/* First Name */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#3B2921]">First Name *</label>
            <input
              type="text"
              {...register("first_name")}
              className="w-full border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs text-[#3B2921] focus:border-[#D96B27] focus:outline-none"
              style={{ borderRadius: "3px" }}
            />
            {errors.first_name && <p className="text-[11px] text-[#B94E27]">{errors.first_name.message}</p>}
          </div>

          {/* Last Name */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#3B2921]">Last Name *</label>
            <input
              type="text"
              {...register("last_name")}
              className="w-full border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs text-[#3B2921] focus:border-[#D96B27] focus:outline-none"
              style={{ borderRadius: "3px" }}
            />
            {errors.last_name && <p className="text-[11px] text-[#B94E27]">{errors.last_name.message}</p>}
          </div>

          {/* Roll Number */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#3B2921]">Roll Number / Matriculation ID *</label>
            <input
              type="text"
              {...register("roll_number")}
              className="w-full border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs font-mono text-[#3B2921] focus:border-[#D96B27] focus:outline-none"
              style={{ borderRadius: "3px" }}
            />
            {errors.roll_number && <p className="text-[11px] text-[#B94E27]">{errors.roll_number.message}</p>}
          </div>

          {/* Email */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#3B2921]">Institutional Email *</label>
            <input
              type="email"
              {...register("email")}
              className="w-full border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs text-[#3B2921] focus:border-[#D96B27] focus:outline-none"
              style={{ borderRadius: "3px" }}
            />
            {errors.email && <p className="text-[11px] text-[#B94E27]">{errors.email.message}</p>}
          </div>

          {/* Phone */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#3B2921]">Contact Phone *</label>
            <input
              type="text"
              {...register("phone")}
              className="w-full border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs text-[#3B2921] focus:border-[#D96B27] focus:outline-none"
              style={{ borderRadius: "3px" }}
            />
            {errors.phone && <p className="text-[11px] text-[#B94E27]">{errors.phone.message}</p>}
          </div>

          {/* Course */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#3B2921]">Course *</label>
            <input
              type="text"
              {...register("course")}
              className="w-full border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs text-[#3B2921] focus:border-[#D96B27] focus:outline-none"
              style={{ borderRadius: "3px" }}
            />
            {errors.course && <p className="text-[11px] text-[#B94E27]">{errors.course.message}</p>}
          </div>

          {/* Semester */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#3B2921]">Semester *</label>
            <input
              type="number"
              min={1}
              step={1}
              {...register("semester", { valueAsNumber: true })}
              className="w-full border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs text-[#3B2921] focus:border-[#D96B27] focus:outline-none"
              style={{ borderRadius: "3px" }}
            />
            {errors.semester && <p className="text-[11px] text-[#B94E27]">{errors.semester.message}</p>}
          </div>

          {/* Academic Class */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-[#3B2921]">Assigned Academic Class</label>
            <select
              {...register("academic_class_id")}
              className="w-full border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs text-[#3B2921] focus:border-[#D96B27] focus:outline-none"
              style={{ borderRadius: "3px" }}
            >
              <option value="">-- Select Class --</option>
              {classList.map((c) => (
                <option key={c.id} value={String(c.id)}>
                  {c.name} {c.academic_year ? `(${c.academic_year})` : ""}
                </option>
              ))}
            </select>
          </div>

        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={busy}
          className="border border-[#B94E27] bg-[#D96B27] px-5 py-2.5 text-xs font-semibold uppercase tracking-wider text-white hover:bg-[#B94E27] disabled:opacity-50"
          style={{ borderRadius: "3px" }}
        >
          {busy ? "Submitting..." : submitLabel}
        </button>

        <Link
          href="/students"
          className="border border-[#E8D8BD] bg-[#FFF8E7] px-5 py-2.5 text-xs font-semibold uppercase tracking-wider text-[#3B2921] hover:border-[#D96B27]"
          style={{ borderRadius: "3px" }}
        >
          Cancel
        </Link>
      </div>
    </form>
  );
}