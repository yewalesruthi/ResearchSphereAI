export interface User {
  id: number;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Workspace {
  id: number;
  name: string;
  description: string | null;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: number;
  workspace_id: number;
  filename: string;
  file_type: string;
  page_count: number;
  chunk_count: number;
  file_size_bytes: number;
  created_at: string;
}

export interface ImageFile {
  id: number;
  workspace_id: number;
  filename: string;
  extracted_text: string | null;
  chunk_count: number;
  file_size_bytes: number;
  created_at: string;
}

export interface AudioFile {
  id: number;
  workspace_id: number;
  filename: string;
  duration_seconds: number;
  chunk_count: number;
  file_size_bytes: number;
  created_at: string;
}

export interface SourceReference {
  document: string;
  page: number | null;
  chunk_id: string;
}

export interface ChatMessage {
  id?: number;
  role: "user" | "assistant";
  content: string;
  sources?: SourceReference[];
  intent?: string;
  created_at?: string;
}

export interface ChatResponse {
  answer: string;
  sources: SourceReference[];
  intent: string;
}

export interface SearchResult {
  chunk_id: string;
  document: string;
  page: number | null;
  text: string;
  score: number;
  vector_score: number;
  bm25_score: number;
}

export interface GraphNode {
  id: string;
  label: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
}

export interface KnowledgeGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface DashboardStats {
  document_count: number;
  image_count: number;
  audio_count: number;
  storage_bytes: number;
  recent_messages: ChatMessage[];
}

export interface TimestampReference {
  file: string;
  start: string;
  end: string;
}

export interface Settings {
  llmModel: string;
  embeddingModel: string;
  groqApiKey: string;
}
