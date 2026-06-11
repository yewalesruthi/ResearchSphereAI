"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Mic, Upload, Loader2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface AudioUploadProps {
  onUpload: (file: File) => Promise<void>;
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function audioBufferToWav(buffer: AudioBuffer): Blob {
  const numChannels = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;
  const format = 1;
  const bitDepth = 16;
  const samples = buffer.length;
  const blockAlign = (numChannels * bitDepth) / 8;
  const byteRate = sampleRate * blockAlign;
  const dataSize = samples * blockAlign;
  const bufferLength = 44 + dataSize;
  const arrayBuffer = new ArrayBuffer(bufferLength);
  const view = new DataView(arrayBuffer);

  const writeString = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
  };

  writeString(0, "RIFF");
  view.setUint32(4, bufferLength - 8, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, format, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);
  writeString(36, "data");
  view.setUint32(40, dataSize, true);

  let offset = 44;
  for (let i = 0; i < samples; i++) {
    for (let ch = 0; ch < numChannels; ch++) {
      const sample = Math.max(-1, Math.min(1, buffer.getChannelData(ch)[i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
      offset += 2;
    }
  }

  return new Blob([arrayBuffer], { type: "audio/wav" });
}

async function recordingBlobToWavFile(blob: Blob): Promise<File> {
  const arrayBuffer = await blob.arrayBuffer();
  const audioContext = new AudioContext();
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
  await audioContext.close();
  const wavBlob = audioBufferToWav(audioBuffer);
  return new File([wavBlob], `recording-${Date.now()}.wav`, { type: "audio/wav" });
}

export function AudioUpload({ onUpload }: AudioUploadProps) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [duration, setDuration] = useState(0);
  const [recordedFile, setRecordedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const clearPreview = useCallback(() => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setRecordedFile(null);
  }, [previewUrl]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      streamRef.current?.getTracks().forEach((t) => t.stop());
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const handleFile = useCallback(
    async (file: File) => {
      setUploading(true);
      setError(null);
      setSuccess(false);
      clearPreview();
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
    [onUpload, clearPreview]
  );

  const startRecording = async () => {
    setError(null);
    clearPreview();
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mimeType = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/mp4";
      const recorder = new MediaRecorder(stream, { mimeType });
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
        const blob = new Blob(chunksRef.current, { type: mimeType });
        try {
          const wavFile = await recordingBlobToWavFile(blob);
          setRecordedFile(wavFile);
          setPreviewUrl(URL.createObjectURL(wavFile));
        } catch {
          setError("Failed to process recording. Please try again.");
        }
        setIsRecording(false);
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
      setDuration(0);
      timerRef.current = setInterval(() => setDuration((d) => d + 1), 1000);
    } catch {
      setError("Microphone access denied. Please allow microphone permission in your browser.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  };

  const uploadRecording = async () => {
    if (!recordedFile) return;
    await handleFile(recordedFile);
    clearPreview();
  };

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
          <h3 className="mt-4 font-semibold">Audio</h3>
          <p className="mt-1 text-sm text-muted-foreground">MP3, WAV, M4A</p>

          {!isRecording && !recordedFile && (
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              <input
                type="file"
                accept=".mp3,.wav,.m4a"
                className="hidden"
                id="upload-audio"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFile(file);
                }}
              />
              <Button variant="outline" asChild disabled={uploading}>
                <label htmlFor="upload-audio" className="cursor-pointer">
                  Choose File
                </label>
              </Button>
              <Button variant="outline" onClick={startRecording} disabled={uploading}>
                <Mic className="h-4 w-4" />
                Record Audio
              </Button>
            </div>
          )}

          {isRecording && (
            <div className="mt-4 flex flex-col items-center gap-3">
              <p className="flex items-center gap-2 text-sm font-medium text-destructive">
                <span className="h-2 w-2 animate-pulse rounded-full bg-destructive" />
                Recording... {formatDuration(duration)}
              </p>
              <Button variant="destructive" onClick={stopRecording}>
                Stop Recording
              </Button>
            </div>
          )}

          {recordedFile && previewUrl && !isRecording && (
            <div className="mt-4 flex w-full max-w-sm flex-col items-center gap-3">
              <audio src={previewUrl} controls className="w-full" />
              <div className="flex gap-2">
                <Button onClick={uploadRecording} disabled={uploading}>
                  Upload Recording
                </Button>
                <Button variant="outline" onClick={clearPreview} disabled={uploading}>
                  Discard
                </Button>
              </div>
            </div>
          )}

          {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
        </div>
      </CardContent>
    </Card>
  );
}
