import {
  mockCards,
  mockContactCard,
  mockCrawlResponse,
  mockDetails,
  mockFit,
  mockHarvestResponse
} from "@/lib/mock-data";
import type {
  ConfirmProfessor,
  ContactCard,
  CrawlResponse,
  FitResult,
  HarvestDepartmentResponse,
  ProfessorCard,
  ProfessorDetail
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== "false";

type CrawlInput = {
  university: string;
  department: string;
  url: string;
};

async function pause(ms = 450) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {})
    }
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `API 요청에 실패했습니다. (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export async function crawlDepartment(input: CrawlInput): Promise<CrawlResponse> {
  if (USE_MOCKS) {
    await pause();
    return {
      ...mockCrawlResponse,
      department: {
        ...mockCrawlResponse.department,
        university: input.university || mockCrawlResponse.department.university,
        department: input.department || mockCrawlResponse.department.department,
        source_url: input.url || mockCrawlResponse.department.source_url
      }
    };
  }

  return request<CrawlResponse>("/api/departments/crawl", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export async function confirmProfessors(departmentId: number, professors: ConfirmProfessor[]): Promise<CrawlResponse> {
  if (USE_MOCKS) {
    await pause(250);
    return {
      ...mockCrawlResponse,
      professors: professors
        .filter((professor) => !professor.excluded)
        .map((professor, index) => ({
          ...mockCrawlResponse.professors[index],
          ...professor,
          id: mockCrawlResponse.professors[index]?.id ?? index + 1,
          department_id: departmentId,
          university: mockCrawlResponse.department.university,
          department: mockCrawlResponse.department.department,
          source_url: mockCrawlResponse.department.source_url,
          analysis_type: mockCrawlResponse.professors[index]?.analysis_type ?? "data_limited",
          evidence_confidence: mockCrawlResponse.professors[index]?.evidence_confidence ?? "low",
          created_at: mockCrawlResponse.professors[index]?.created_at ?? new Date().toISOString()
        }))
    };
  }

  return request<CrawlResponse>(`/api/departments/${departmentId}/professors/confirm`, {
    method: "POST",
    body: JSON.stringify({ professors })
  });
}

export async function harvestDepartment(departmentId: number): Promise<HarvestDepartmentResponse> {
  if (USE_MOCKS) {
    await pause(900);
    return mockHarvestResponse;
  }

  return request<HarvestDepartmentResponse>(`/api/departments/${departmentId}/papers/harvest`, {
    method: "POST"
  });
}

export async function fetchProfessorCards(departmentId: number): Promise<ProfessorCard[]> {
  if (USE_MOCKS) {
    await pause(250);
    return mockCards;
  }

  return request<ProfessorCard[]>(`/api/departments/${departmentId}/professors`);
}

export async function fetchProfessorDetail(professorId: number): Promise<ProfessorDetail> {
  if (USE_MOCKS) {
    await pause(250);
    return mockDetails[professorId] ?? mockDetails[1];
  }

  return request<ProfessorDetail>(`/api/professors/${professorId}`);
}

export async function analyzeFit(professorId: number, userInterest: string): Promise<FitResult> {
  if (USE_MOCKS) {
    await pause(350);
    return mockFit(professorId, userInterest);
  }

  return request<FitResult>(`/api/professors/${professorId}/fit`, {
    method: "POST",
    body: JSON.stringify({ user_interest: userInterest })
  });
}

export async function fetchContactCard(professorId: number, userInterest: string): Promise<ContactCard> {
  if (USE_MOCKS) {
    await pause(350);
    return mockContactCard(professorId, userInterest);
  }

  return request<ContactCard>(`/api/professors/${professorId}/contact-card`, {
    method: "POST",
    body: JSON.stringify({ user_interest: userInterest })
  });
}

export function isMockMode() {
  return USE_MOCKS;
}
