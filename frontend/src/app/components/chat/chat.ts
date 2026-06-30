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
        this.api.addToHistory('assistant', res.answer, res.sources || []);
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
}