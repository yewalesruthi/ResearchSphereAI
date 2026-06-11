"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { FileUpload } from "@/components/upload/FileUpload";
import { AudioUpload } from "@/components/upload/AudioUpload";
import { useWorkspaceStore } from "@/store/workspaceStore";
import api from "@/lib/api";

export default function UploadPage() {
  const currentWorkspace = useWorkspaceStore((s) => s.currentWorkspace);

  const uploadWithForm = async (endpoint: string, file: File) => {
    if (!currentWorkspace) throw new Error("No workspace selected");
    const formData = new FormData();
    formData.append("workspace_id", String(currentWorkspace.id));
    formData.append("file", file);
    await api.post(endpoint, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  };

  if (!currentWorkspace) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center p-8">
          <p className="text-muted-foreground">Select or create a workspace first.</p>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="p-8">
        <h1 className="mb-2 text-3xl font-bold">Upload</h1>
        <p className="mb-8 text-muted-foreground">
          Upload documents, images, or audio to your workspace
        </p>
        <div className="grid gap-6 lg:grid-cols-3">
          <FileUpload
            accept=".pdf,.docx,.pptx,.txt"
            label="Documents"
            description="PDF, DOCX, PPTX, TXT"
            onUpload={(file) => uploadWithForm("/documents/upload", file)}
          />
          <FileUpload
            accept=".png,.jpg,.jpeg,.tiff,.bmp"
            label="Images"
            description="PNG, JPG, JPEG, TIFF, BMP"
            onUpload={(file) => uploadWithForm("/images/upload", file)}
          />
          <AudioUpload onUpload={(file) => uploadWithForm("/audio/upload", file)} />
        </div>
      </div>
    </AppLayout>
  );
}
