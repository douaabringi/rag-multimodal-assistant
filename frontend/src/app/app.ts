import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UploadComponent } from './components/upload/upload';
import { ChatComponent } from './components/chat/chat';
import { DocumentsComponent } from './components/documents/documents';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, UploadComponent, ChatComponent, DocumentsComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent {
  activeTab = 'chat';
}