export type ProcessingStatus = "PENDING" | "PROCESSING" | "SUCCESS" | "FAILED";

export interface DocumentUploadResponse {
  document_id: string;
  task_id: string;
  filename: string;
  file_size: number;
  status: ProcessingStatus;
  message: string;
}

export interface DocumentStatusResponse {
  document_id: string;
  filename: string;
  file_ext: string;
  file_size: number;
  status: ProcessingStatus;
  task_id: string | null;
  num_chunks: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentListItem {
  document_id: string;
  filename: string;
  file_ext: string;
  file_size: number;
  status: ProcessingStatus;
  num_chunks: number | null;
  created_at: string;
}
