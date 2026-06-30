import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrls: ['./chat.css']
})
export class ChatComponent implements OnInit {
  currentQuestion = '';
  isLoading = false;
  isTyping = false;
  selectedDocument: string = '';
  availableDocuments: any[] = [];
  showFavorites = false;
  draggedMessage: any = null;

  suggestions = [
    'De quoi parle ce document ?',
    'Résume les points principaux',
    'Quelles sont les classes du diagramme UML ?',
    'Explique l\'architecture du système'
  ];

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.api.getDocuments().subscribe((res: any) => {
      this.availableDocuments = res.documents;
      this.cdr.detectChanges();
    });
  }

  get messages() {
    return this.api.getHistory();
  }

  get favorites() {
    return this.api.getFavorites();
  }

  useSuggestion(suggestion: string) {
    this.currentQuestion = suggestion;
    this.sendMessage();
  }

  sendMessage() {
    if (!this.currentQuestion.trim() || this.isLoading) return;

    this.api.addToHistory('user', this.currentQuestion);
    const question = this.currentQuestion;
    this.currentQuestion = '';
    this.isLoading = true;
    this.isTyping = true;
    this.cdr.detectChanges();

    const filter = this.selectedDocument || null;

    this.api.askQuestion(question, this.messages, filter).subscribe({
      next: (res: any) => {
        this.isTyping = false;
        this.api.addToHistory('assistant', res.answer, res.sources || [], res.confidence || null);
        this.isLoading = false;
        this.cdr.detectChanges();
        this.scrollToBottom();
      },
      error: () => {
        this.isTyping = false;
        this.api.addToHistory('assistant', '❌ Erreur — vérifie que FastAPI tourne.');
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  clearHistory() {
  this.api.saveCurrentSession();
  this.api.clearHistory();
  this.cdr.detectChanges();
}

  scrollToBottom() {
    setTimeout(() => {
      const chat = document.querySelector('.messages');
      if (chat) chat.scrollTop = chat.scrollHeight;
    }, 100);
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  // ── Favoris ──────────────────────────────────────
  toggleFavorite(msg: any) {
    this.api.toggleFavorite(msg);
    this.cdr.detectChanges();
  }

  toggleFavoritesPanel() {
    this.showFavorites = !this.showFavorites;
    this.cdr.detectChanges();
  }

  // ── Glisser-déposer pour ajouter aux favoris ─────
  onDragStart(msg: any) {
    this.draggedMessage = msg;
  }

  onDragEnd() {
    this.draggedMessage = null;
  }

  onFavoriteZoneDragOver(event: DragEvent) {
    event.preventDefault();
  }

  onFavoriteZoneDrop(event: DragEvent) {
    event.preventDefault();
    if (this.draggedMessage && !this.draggedMessage.favorite) {
      this.toggleFavorite(this.draggedMessage);
    }
    this.draggedMessage = null;
  }

  showSessionHistory = false;

  get sessionHistory() {
    return this.api.getSessionHistory();
  }

  toggleSessionHistory() {
    this.showSessionHistory = !this.showSessionHistory;
    this.cdr.detectChanges();
  }

  loadSession(sessionId: number) {
    this.api.loadSession(sessionId);
    this.showSessionHistory = false;
    this.cdr.detectChanges();
    this.scrollToBottom();
  }

  deleteSession(sessionId: number, event: Event) {
    event.stopPropagation();
      this.api.deleteSession(sessionId);
  this.cdr.detectChanges();
  }
}