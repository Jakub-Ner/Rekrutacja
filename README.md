Napisz API do zarządzania rezerwacjami stolików w restauracji.

W [pliku](https://github.com/Solvro/Rekrutacja/blob/master/backend/seats.json) JSON znajduje się lista stolików w restauracji. Każdy stolik ma  przypisany swój numer oraz minimalną i maksymalną liczbę miejsc.



### Endpointy do zaimplementowania:

Wszystkie endpointy powinny być zaimplementowane zgodnie z [specyfikacją](https://github.com/Solvro/Rekrutacja/blob/master/backend/api-spec.yaml). Specyfikacja nie definiuje wszystkich odpowiedzi HTTP. Wybierz właściwe kody statusów, w zależności od sposobu realizacji zapytania.

#### 

#### Składanie rezerwacji.

- Zapytanie POST: `/reservations`.
- Endpoint pozwala klientowi na złożenie nowej rezerwacji na stolik.
- Istotne jest, aby przed zapisaniem rezerwacji sprawdzić poprawność wszystkich danych, oraz dostępność stolika w wybranym czasie.
- Po udanej rezerwacji należy wysłać wiadomość na podany przez  użytkownika adres e-mail. W wiadomości powinny znaleźć się wszystkie  dane oraz unikalny numer rezerwacji. Do wysyłania "fake maili" możesz skorzystać z [Ethereal](https://ethereal.email/).
- Należy zwrócić właściwą odpowiedź HTTP i zapisać rezerwację bazie danych.

#### 

#### Pobranie listy rezerwacji danego dnia

- Zapytanie GET: `/reservations`
- Endpoint pozwala pracownikom restauracji na pobranie listy wszystkich rezerwacji danego dnia.

#### 

#### Wysłanie prośby o anulowanie rezerwacji

- Zapytanie PUT: `/reservations/{id}`
- Endpoint pozwala klientowi na wysłanie prośby o anulowanie rezerwacji.
- Użytkownik w parametrze zapytania wysyła unikalne id rezerwacji, które otrzymał na maila.
- W treści zapytania wysyłana jest prośba o zmianę statusu rezerwacji na wartość "requested cancellation".
- Rezerwacja może zostać anulowana najpóźniej 2 godziny przed godziną na którą został zarezerwowany stolik.
- Jeśli anulowanie jest możliwe należy wysłać wiadomość e-mail na  adres użytkownika. W treści maila należy umieścić 6-cyfrowy kod  weryfikacyjny, który służy do potwierdzenia tożsamości.

#### 

#### Potwierdzenie anulowania rezerwacji

- Zapytanie DELETE: `/reservations/{id}`
- Endpoint służy do potwierdzenia anulowania rezerwacji.
- W treści zapytania użytkownik wysyła kod weryfikacyjny, który otrzymał w wiadomości e-mail.
- Jeżeli kod jest poprawny i możliwe jest anulowanie rezerwacji, to  należy usunąć ją z bazy danych i potwierdzić anulowanie e-mailem.

#### 

#### Pobranie listy wolnych stolików

- Zapytanie GET: `/tables`
- Endpoint pozwala klientowi na pobranie listy wszystkich dostępnych  do rezerwacji stolików w określonym czasie i z odpowiednią liczbą  miejsc.
