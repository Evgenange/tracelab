const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

export interface Dataset {
  id: string;
  project_id: string;
  name: string;
  description: string | null;
  created_at: string;
}

export interface DatasetVersion {
  id: string;
  dataset_id: string;
  version_number: number;
  original_filename: string;
  sha256: string;
  file_size_bytes: number;
  status: string;
  created_at: string;
}

export interface QualityReport {
  id: string;
  dataset_version_id: string;
  row_count: number;
  column_count: number;
  duplicate_row_count: number;
  null_count: number;
  column_schema: Record<string, string>;
  null_counts_json: Record<string, number>;
  numeric_summary_json: Record<
    string,
    {
      min: number;
      max: number;
      mean: number;
      median: number;
    }
  >;
  created_at: string;
}

export interface Provenance {
  dataset_version_id: string;
  dataset_id: string;
  version_number: number;
  original_filename: string;
  sha256: string;
  file_size_bytes: number;
  version_status: string;
  version_created_at: string;
  processing_job_id: string | null;
  processing_status: string | null;
  processing_started_at: string | null;
  processing_completed_at: string | null;
  quality_report_id: string | null;
  quality_report_created_at: string | null;
  pipeline_name: string;
  pipeline_version: string;
}

async function handleResponse<T>(
  response: Response,
): Promise<T> {
  if (!response.ok) {
    const body = await response.text();

    throw new Error(
      body ||
        `Request failed with status ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
}

export async function getProjects(): Promise<Project[]> {
  const response = await fetch(
    `${API_BASE_URL}/projects`,
  );

  return handleResponse<Project[]>(response);
}

export async function getDatasets(
  projectId: string,
): Promise<Dataset[]> {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/datasets`,
  );

  return handleResponse<Dataset[]>(response);
}

export async function createDataset(
  projectId: string,
  name: string,
  description: string | null = null,
): Promise<Dataset> {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/datasets`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name,
        description,
      }),
    },
  );

  return handleResponse<Dataset>(response);
}

export async function getDatasetVersions(
  datasetId: string,
): Promise<DatasetVersion[]> {
  const response = await fetch(
    `${API_BASE_URL}/datasets/${datasetId}/versions`,
  );

  return handleResponse<DatasetVersion[]>(response);
}

export async function uploadDatasetVersion(
  datasetId: string,
  file: File,
): Promise<DatasetVersion> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/datasets/${datasetId}/versions`,
    {
      method: "POST",
      body: formData,
    },
  );

  return handleResponse<DatasetVersion>(response);
}

export async function getQualityReport(
  versionId: string,
): Promise<QualityReport> {
  const response = await fetch(
    `${API_BASE_URL}/dataset-versions/${versionId}/quality`,
  );

  return handleResponse<QualityReport>(response);
}

export async function getProvenance(
  versionId: string,
): Promise<Provenance> {
  const response = await fetch(
    `${API_BASE_URL}/dataset-versions/${versionId}/provenance`,
  );

  return handleResponse<Provenance>(response);
}