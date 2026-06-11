"use client";

import { useCallback, useState } from "react";
import { Upload, Loader2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface FileUploadProps {
  accept: string;
  label: string;
  description: string;
  onUpload: (file: File) => Promise<void>;
}

export function FileUpload({ accept, label, description, onUpload }: FileUploadProps) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    async (file: File) => {
      setUploading(true);
      setError(null);
      setSuccess(false);
      try {
        await onUpload(file);
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [onUpload]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <Card>
      <CardContent className="p-6">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={cn(
            "flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors",
            dragging ? "border-primary bg-primary/5" : "border-muted-foreground/25"
          )}
        >
          {uploading ? (
            <Loader2 className="h-10 w-10 animate-spin text-primary" />
          ) : success ? (
            <CheckCircle className="h-10 w-10 text-green-500" />
          ) : (
            <Upload className="h-10 w-10 text-muted-foreground" />
          )}
          <h3 className="mt-4 font-semibold">{label}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{description}</p>
          <input
            type="file"
            accept={accept}
            className="hidden"
            id={`upload-${label}`}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
            }}
          />
          <Button variant="outline" className="mt-4" asChild disabled={uploading}>
            <label htmlFor={`upload-${label}`} className="cursor-pointer">
              Choose File
            </label>
          </Button>
          {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
        </div>
      </CardContent>
    </Card>
  );
}
