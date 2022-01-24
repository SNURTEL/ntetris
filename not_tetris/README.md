## Spis treści

1. Cel projektu
2. Plan realizacji
3. Zastosowane technologie
4. Struktura projektu
5. Podręcznik użytkownika
6. Problemy w realizacji i ograniczenia systemowe
7. Możliwe dalsze modyfikacje
8. Refleksje na temat projektu (od autora)

## Cel projektu

Celem projektu była realizacja gry Tetris w języku Python. Zostały określone wymagania:

- Interfejs konsolowy gry
- Możliwość ustawienia poziomu trudności
- Zapisywanie osiągniętego przez gracza wyniku

## Plan realizacji

Założona została realizacja projektu zgodnie z metodyką _waterfall_ wg następującego planu:

1. Opracowanie szkieletów komponentów wykorzystywanych dalej do implementacji logiki gry
    * Konsultacja struktury projektu z prowadzącym
2. Implementacja podstawowych mechanizmów gry, w tym:
    * Podstawowych komponentów planszy:
        * Główna klasa planszy
        * Płytki
        * _Tetrimina_
        * Podstawowej logiki planszy:
        * Przemieszczanie i obracanie _tetrimin_
        * System kolizji
3. Opracowanie interfejsu graficznego
4. Rozbudowa logiki planszy do docelowego poziomu, w tym:
    * Implementacja stanów planszy
    * Implementacja mechanizmu usuwania pełnych rzędów
5. Implementacja logiki gry
6. Implementacja stanów gry
7. Implementacja systemu punktacji
8. Realizacja dodatkowej funkcjonalności, w tym:
    * Obsługa wywołań programu z dodatkowymi argumentami
    * Mechanizm informowania użytkownika o konieczności zwiększenia rozmiaru okna konsoli

## Zastosowane technologie

Program napisany został w języku Python w wersji 3.8 i jest przewidziany dla systemów unixowych. Za obsługę wejścia z
klawiatury odpowiada moduł _keyboard_; konsolowy interfejs graficzny zrealizowany został z użyciem wbudowanej
biblioteki _curses_.

## Struktura projektu:

Program składa się z następujących komponentów:

* Plik tetris.py
    * Odpowiada za uruchamianie programu
* Plik game.py
    * Przechowuje logikę gry
    * Klasa GameState:
        * Abstrakcyjna klasa bazowa służąca do definiowania stanów gry. Klasy dziedziczące po GameState określają własne sposoby obsługi zdarzeń, aktualizacji ekranu, powiadamiania odpowiednich części UI o konieczności aktualizacji, oraz wykonują konkretny zestaw czynności po wejściu w dany stan
    * Klasy dziedziczące po GameState:
        * Active, Ended, Paused, StartMenu, Countdown oraz WindowTooSmall
        * Definiują zachowanie gry (kolejno) podczas rozgrywki, po zakończeniu rozgrywki, po zatrzymaniu, w menu głównym, w oczekiwaniu na wznowienie, oraz w sytuacji, kiedy okno terminala jest zbyt małe, aby wyświetlić cały interfejs
    * Klasa Game
        * Klasa kontrolująca logikę gry. Zawiera główną pętlę obsługi zdarzeń, posiada szereg metod zarządzających rozgrywką, potrafi przełączać się między stanami (GameState), oraz przechowuje obiekty obserwowalne skojarzone z elementami UI
* Plik components.py
    * Zawiera komponenty i logikę planszy
    * Klasa BoardState:
        * Abstrakcyjna klasa bazowa służąca do definiowania stanów planszy (powiązanych z aktualnym zachowaniem umieszczanego bloku). Klasy dziedziczące po BoardState definiują własne metody aktualizacji stanu planszy oraz obsługi wejścia z klawiatury
    * Klasy dziedziczące po BoardState:
        * Falling, SoftDrop, HardDrop
        * Wpływają na logikę planszy w sytuacjach (kolejno) swobodnego spadku bloku, przyspieszonego spadku bloku, oraz natychmiastowego upuszczenia bloku
    * Klasa Component:
        * Abstrakcyjna klasa bazowa, po której dziedziczą wszystkie obiekty składające się na planszę. Klasy dziedziczące po Component określa metodę aktualizacji własnego staniu oraz wyświetlania komponentu w UI, ponadto przechowują referencje na obiekt gry
    * Klasy dziedziczące po Component:
        * Klasa Tile:
            * Reprezentuje pojedynczą płytkę na planszy Tetrisa. Z płytek budowane są obiekty klasy Block, a po umieszczeniu bloku na planszy płytki przenoszone są do klasy Board
        * Klasa Block:
            * Reprezentuje blok składający się z płytek, podczas aktualizacji bądź rysowania wywołuje odpowiednie metody na każdej z nich. Może być przemieszczany i obracany, oraz jest w stanie wykrywać kolizje z płytkami na planszy. Posiada własny licznik punktów (inkrementowany podczas przemieszczania bloku przez soft drop lub hard drop), wartość licznika jest dodawana do ogólnej liczby punktów w grze w momencie umieszczenia bloku na planszy. Blok może być stworzony wg jednego z siedmiu wzorów reprezentujących tetrimina, identyfikator wzoru podawany jest w konstruktorze klasy. 
        * Klasa Board:
            * Główna klasa zarządzająca planszą. Kontroluje aktualizacje pola do gry, przechowuje obecnie umieszczany oraz następny w kolejce blok oraz płytki, które zostały już umieszczone na planszy. 
* Plik ui.py
    * Przechowuje komponenty konsolowego interfejsu graficznego 
    * Klasa Drawable:
        * Abstrakcyjna klasa bazowa, po której dziedziczą wszystkie komponenty interfejsu graficznego. Klasy potomne do Drawable określają własne metody wyświetlania komponentu w interfejsie oraz przechowują referencje do obiektu gry
    * Klasy dziedziczące po Drawable:
        * Klasa Box
            * Klasa reprezentująca prostokątny panel w interfejsie graficznym. Na ekranie wyświetlana jako subwindow
        * Klasa Frame
            * Klasa reprezentująca pusty w środku prostokąt. Może posiadać tytuł będący instancją klasy TextField. Na ekranie wyświetlana jako subwindow
        * Klasa TextField
            * Klasa reprezentująca pole tekstowe. Posiada metody aktualizacji zarówno w sposób bezpośredni, jak i przez wewnętrzną klasę TextFieldObserver
        * Klasa TextFieldObserver
            * Obserwator, który może być skojarzony z obiektem obserwowalnym. Umożliwia aktualizacje pola tekstowego przez podanie odpowiednich argumentów przekazywanych przez słowa kluczowe podczas wysyłania sygnału z obiektu obserwowalnego
    * Klasy dziedziczące po TextField:
        * Scoreboard
            * Specjalna klasa potomna do TextField, w której dostosowano metodę modyfikacji zawartości pola tekstowego, aby była ona automatycznie formatowana do postaci tabeli wyników
        * Countdown
            * Specjalna klasa potomna do TextField, w której dostosowano metodę modyfikacji zawartości pola tekstowego, aby pozwalała na generowanie odpowiedniego komunikatu podczas odliczania do wznowienia / rozpoczęcia gry na podstawie liczby pozostałych ticków
        * GameEnded
            * Specjalna klasa potomna do TextField, w której dostosowano metodę modyfikacji zawartości pola tekstowego, aby możliwe było generowanie komunikatu informującego o zakończeniu gry na podstawie wyniku osiągniętego przez gracza
* Plik class_models.py
    * Przechowuje abstrakcje oraz klasy wykorzystywane w więcej niż jednym module
    * Klasa Observable:
        * Obiekt obserwowalny. Posiada metody umożliwiające dodawanie i usuwanie obserwatorów, ustawiania flagi ‘zmieniono’, oraz powiadamiania każdego obserwatora o zmianie, jeśli flaga została uprzednio ustawiona. Klasa Observable nie jest abstrakcją i może być używana w takiej formie, jaka została zdefiniowana w pliku class_models.py
    * Klasa Observer:
        * Abstrakcyjna klasa bazowa obserwatora. Obserwator może zostać skojarzony z obiektem obserwowalnym, a każda klasa potomna do Observer określa własną metodę aktualizacji obiektu, w którym się znajduje (dane potrzebne do aktualizacji mogą zostać pobrane w sposób bezpośredni z referencji na obiekt obserwowalny, który wywołał aktualizację, lub przekazane przez argumenty ze słowem kluczowym)
* Plik settings.py
    * Plik konfiguracyjny, przechowujący stałe regulujące działanie gry, takie jak częstotliwość aktualizacji stanu gry czy wymiary okna. Zawartość pliku nie powinna być modyfikowana przez użytkownika końcowego
* Plik scoreboard.json
    * Przechowuje tabelę wyników gry.



## Podręcznik użytkownika

Grę należy uruchomić z poziomu konsoli używając polecenia:

```
sudo python3 tetris.py
```

Dodatkowo mogą zostać przekazane flagi:

```
--level LEVEL    # pomija menu główne i rozpoczyna grę na danym poziomie
--clear-scoreboard    # podczas uruchamiania gry resetuje tabelę wyników
```

Instrukcje sterowania są na bieżąco wyświetlane na ekranie. Po zakończeniu gry aktualny wynik jest zapisywany, jeśli
jest on wśród dziesięciu najwyższych wyników osiągniętych przez gracza.

## Problemy w realizacji oraz ograniczenia systemowe

* Niemożliwa była implementacja gry w prosty sposób dla systemu Windows z uwagi na specyfikę programu Windows
  PowerShell, który nie pozwala on na zmianę koloru tekstu w konsoli. Ponadto biblioteka _curses_ nie jest dostępna na
  tej platformie, przez co konieczne byłoby stosowanie zamienników – wobec tego realizacja została ograniczona do
  systemów unixowych.
* Do działania gry konieczna jest możliwość sprawdzenia, czy dowolny klawisz jest wciśnięty w danym momencie, czego nie
  da się osiągnąć z pomocą funkcji _getch()_ z biblioteki _curses_, która jest w stanie jedynie odczytywać wciśnięte
  klawisze z wejścia standardowego. W efekcie wynik wywołania funkcji zależny jest od częstotliwości raportowania
  klawiatury i opóźnienia powtarzania znaku. Rozwiązanie problemu możliwe było przez skorzystanie z systemu X Server do
  przechwytywania naciśnięć klawiszy, lub wykorzystanie modułu pozwalającego na bezpośredni dostęp do klawiatury –
  wybrany został moduł _keyboard_ z uwagi na prostotę implementacji, alternatywnie można było zastosować _pynput_. Wadą
  takiego rozwiązania jest konieczność uruchamiania gry poprzez polecenie _sudo_, gdyż dostęp do urządzeń znajdujących
  się w katalogu _/dev_ możliwy jest tylko z uprawnieniami roota.
* Biblioteka curses posiada pewne ograniczenia w zakresie obsługi sytuacji, w których zmieniony został rozmiar okna
  konsoli – wobec tego, po zmniejszeniu go poniżej rozmiaru wymaganego do działania gry, a następnie powiększeniu,
  niektóre elementy interfejsu mogą być wyświetlane w sposób niepoprawny.

## Możliwe dalsze modyfikacje

* Rozbudowa logiki gry, aby spełniała wytyczne _Tetris Guidelines_ z 2009 roku, na co składa się między innymi
  implementacja systemu _Super Rotation System_, rozpoznawanie ruchu _T-Spin_, oraz zmiana mapowania klawiszy
* Optymalizacja mechanizmu rysowania interfejsu – w chwili obecnej podczas aktualizacji ekranu cały interfejs jest
  wymazywany i rysowany ponownie, zamiast aktualizacji jedynie tych linii i kolumn, które uległy modyfikacji
* Implementacja dynamicznego skalowania interfejsu
* Dalsza refaktoryzacja kodu celem poprawy czytelności i wydajności

## Refleksje na temat projektu (od autora)
Był to mój pierwszy projekt o usystematyzowanej strukturze i metodyce pracy napisany w Pythonie. Szczególnie zadowolony jestem z zastosowania wzorców projektowych State, Composite i Observer, które miało odzwierciedlenie w czytelności kodu. Z procesu tworzenia gry wyniosłem przede wszystkim wiedzę ogólną o projektach – w szczególności dotyczącą struktury kodu i budowy poszczególnych komponentów. Przy ponownej realizacji projektu podobnej skali położyłbym większy nacisk na wstępne rozplanowanie każdego elementu programu i trzymanie się tego planu przez cały okres realizacji – w obecnym projekcie odejście od planu nastąpiło siłą rzeczy, z uwagi na ciągły przyrost wiedzy – pisząc szkielety komponentów nie mogłem np. zastosować wzorca Observer, gdyż o jego istnieniu dowiedziałem się dopiero w końcowej fazie realizacji projektu. Na większą uwagę zasłużyłby też system obsługi zdarzeń – należałoby go zrealizować raczej przez generowanie obiektów klasy Event i ich przetwarzanie, niż sprawdzanie szeregu warunków w każdej iteracji pętli obsługi zdarzeń (co swoją drogą umożliwiłoby bardziej poprawną implementację niektórych wzorców oraz znaczne uproszczenie części funkcji). Mimo to, uznaję ten projekt za udany – projekt spełnia postawione założenia, implementację można uznać za wystarczająco dobrą (przy uwzględnieniu poziomu umiejętności zmieniającego się podczas realizacji projektu), a ja, jako autor, jestem usatysfakcjonowany rezultatem.

