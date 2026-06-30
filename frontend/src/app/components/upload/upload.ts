import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.html',
  styleUrls: ['./upload.css']
})
export class UploadComponent {
  isLoading = false;
  message = '';
  success = false;
  isDragging = false;
  progress = 0;
  selectedFile: File | null = null;
  previewUrl: string | null = null;

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragging = true;
    this.cdr.detectChanges();
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
    this.cdr.detectChanges();
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
    const file = event.dataTransfer?.files[0];
    if (file) this.processFile(file);
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) this.processFile(file);
  }

  processFile(file: File) {
    this.selectedFile = file;
    this.message = '';
    this.previewUrl = null;

    // Aperçu image
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.previewUrl = e.target.result;
        this.cdr.detectChanges();
      };
      reader.readAsDataURL(file);
    }

    this.cdr.detectChanges();
  }

  uploadFile() {
    if (!this.selectedFile || this.isLoading) return;

    this.isLoading = true;
    this.progress = 0;
    this.message = '';
    this.cdr.detectChanges();

    // Simulation de progression
    const interval = setInterval(() => {
      if (this.progress < 85) {
        this.progress += Math.random() * 15;
        this.cdr.detectChanges();
      }
    }, 400);

    this.api.uploadDocument(this.selectedFile).subscribe({
      next: (res: any) => {
        clearInterval(interval);
        this.progress = 100;
        this.isLoading = false;
        this.success = true;
        this.message = `"${res.filename}" indexé avec succès — ${res.chunks_count} segments créés`;
        this.cdr.detectChanges();
        setTimeout(() => {
          this.selectedFile = null;
          this.previewUrl = null;
          this.progress = 0;
          this.cdr.detectChanges();
        }, 3000);
      },
      error: (err: any) => {
        clearInterval(interval);
        this.progress = 0;
        this.isLoading = false;
        this.success = false;
        this.message = `Erreur : ${err.error?.detail || 'Upload échoué'}`;
        this.cdr.detectChanges();
      }
    });
  }

  getFileIcon(): string {
    if (!this.selectedFile) return '📄';
    if (this.selectedFile.type === 'application/pdf') return '📕';
    if (this.selectedFile.type.startsWith('image/')) return '🖼️';
    return '📄';
  }

  formatSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }
}