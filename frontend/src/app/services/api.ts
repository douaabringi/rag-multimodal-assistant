import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  uploadDocument(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.baseUrl}/upload`, formData);
  }

  askQuestion(question: string, history: any[], filename: string | null = null): Observable<any> {
  return this.http.post(`${this.baseUrl}/query`, { question, history, filename });
}

  getDocuments(): Observable<any> {
  return this.http.get(`${this.baseUrl}/documents`);
}

  getFileUrl(filename: string): string {
  return `${this.baseUrl}/files/${filename}`;
}

  resetDocuments(): Observable<any> {
    return this.http.delete(`${this.baseUrl}/reset`);
  }

  deleteDocument(filename: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/documents/${encodeURIComponent(filename)}`);
  }

  // Historique persistant
  private chatHistory: any[] = [];

  getHistory(): any[] {
    return this.chatHistory;
  }

  addToHistory(role: string, content: string, sources: any[] = []) {
  this.chatHistory.push({ role, content, sources, timestamp: new Date() });
  }

  clearHistory() {
    this.chatHistory = [];
  }
}