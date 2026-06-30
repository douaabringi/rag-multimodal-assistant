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

  addToHistory(role: string, content: string, sources: any[] = [], confidence: any = null) {
  this.chatHistory.push({ role, content, sources, confidence, timestamp: new Date(), favorite: false });
  }

  clearHistory() {
    this.chatHistory = [];
  }

  // Messages favoris (persistent en mémoire pendant la session)
  private favorites: any[] = [];

  toggleFavorite(message: any) {
    message.favorite = !message.favorite;
    if (message.favorite) {
      this.favorites.push(message);
    } else {
      this.favorites = this.favorites.filter(f => f !== message);
    }
  }

  getFavorites(): any[] {
    return this.favorites;
  }
// Historique des sessions passées
  private sessionHistory: any[] = [];

  saveCurrentSession() {
    if (this.chatHistory.length === 0) return;
    this.sessionHistory.unshift({
      id: Date.now(),
      date: new Date(),
      preview: this.chatHistory[0]?.content?.substring(0, 50) || 'Conversation',
      messages: [...this.chatHistory]
    });
  }

  getSessionHistory(): any[] {
    return this.sessionHistory;
  }

  loadSession(sessionId: number) {
    const session = this.sessionHistory.find(s => s.id === sessionId);
    if (session) {
      this.chatHistory = [...session.messages];
    }
  }

  deleteSession(sessionId: number) {
    this.sessionHistory = this.sessionHistory.filter(s => s.id !== sessionId);
  }

}