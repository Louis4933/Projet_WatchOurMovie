import { Component } from '@angular/core';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  userName: string = 'Dorian';

  onSearchKeyUp(event: any) {
      console.log(event.target.value);
  }

  onSearch() {
      console.log('Recherche effectuée');
  }
}
