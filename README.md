## Spis treści

1. Cel projektu
2. Plan realizacji
3. Zastosowane technologie
4. Struktura projektu
5. Podręcznik użytkownika
6. Problemy w realizacji i ograniczenia systemowe
7. Możliwe dalsze modyfikacje

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

* Plik _tetris.py_
    * Odpowiada za uruchamianie program
* Plik _game.py_
    * Przechowuje logikę gry
* Plik components.py
    * Zawiera komponenty i logikę planszy
* Plik _ui.py_
    * Przechowuje komponenty konsolowego interfejsu graficznego
* Plik _class_models.py_
    * Przechowuje abstrakcje oraz klasy wykorzystywane w więcej niż jednym module
* Plik _settings.py_
    * Plik konfiguracyjny, regulujący działanie gry
* Plik _scoreboard.json_
    * Przechowuje tabelę wyników gry

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
