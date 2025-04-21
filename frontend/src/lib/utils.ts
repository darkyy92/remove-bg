import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export async function removeBackground(file: File, onProgress?: (progress: number) => void): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/api/remove-bg", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server antwortete mit Status: ${response.status}`);
    }

    // Handle the PNG response as a blob
    const imageBlob = await response.blob();
    return URL.createObjectURL(imageBlob);
  } catch (error) {
    console.error("Fehler beim Entfernen des Hintergrunds:", error);
    throw error;
  }
}