import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './documents.html',
  styleUrls: ['./documents.css']
})
export class DocumentsComponent implements OnInit {
  documents: any[] = [];
  isLoading = false;
  deletingFile: string | null = null;

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  ngOnInit() { this.loadDocuments(); }

  loadDocuments() {
    this.isLoading = true;
    this.cdr.detectChanges();
    this.api.getDocuments().subscribe({
      next: (res: any) => {
        this.documents = res.documents;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  deleteOne(filename: string) {
    if (!confirm(`Supprimer "${filename}" ?`)) return;
    this.deletingFile = filename;
    this.cdr.detectChanges();

    this.api.deleteDocument(filename).subscribe({
      next: () => {
        this.documents = this.documents.filter(d => d.filename !== filename);
        this.deletingFile = null;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.deletingFile = null;
        alert('Erreur suppression : ' + err.status);
        this.cdr.detectChanges();
      }
    });
  }

  resetAll() {
    if (!confirm('Supprimer TOUS les documents ?')) return;
    this.api.resetDocuments().subscribe({
      next: () => {
        this.documents = [];
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        alert('Erreur reset: ' + err.status);
      }
    });
  }

  get totalChunks(): number {
    return this.documents.reduce((sum, d) => sum + (d.chunks || 0), 0);
  }
  
  getFileUrl(filename: string): string {
    return this.api.getFileUrl(filename);
  }
  
}

