# Streamlit App z Logowaniem i Rolami Użytkowników

Prosty przykład aplikacji Streamlit z:

- Rejestracją i logowaniem użytkowników  
- Przechowywaniem haseł w pliku JSON (SHA-256)  
- Mechanizmem ról (`user` / `admin`)  
- Panelem administratora do zmiany ról  
- Ochroną fragmentów kodu przez dekorator `@requires_role`  
- Fallbackiem dla `st.experimental_rerun()`

---

## Funkcje

1. **Rejestracja**  
   - Domyślnie każdy nowy użytkownik otrzymuje rolę `user`.  
   - Administrator (`admin`) może przy rejestracji nadawać także rolę `admin`.  

2. **Logowanie / Wylogowanie**  
   - Sesja trzymana w `st.session_state`.  
   - Po zalogowaniu widoczny jest pasek boczny z informacją o użytkowniku i roli.  

3. **Role & Dekorator**  
   - Dekorator `@requires_role("rol1", "rol2", …)` zabezpiecza wybrane funkcje/strony.  
   - Przykładowe strony:  
     - `user_page()` – dostępna dla `user` i `admin`  
     - `admin_panel()` – dostępna tylko dla `admin`  
     - `secret_admin_page()` – dostępna tylko dla `admin`  

4. **Panel Administratora**  
   - Wyświetla listę wszystkich użytkowników i ich ról.  
   - Pozwala adminowi zmieniać rolę dowolnego użytkownika (poza sobą).  

5. **Fallback Rerun**  
   - Funkcja `safe_rerun()` najpierw próbuje `st.experimental_rerun()`,  
   - W razie braku tej metody rzuca wewnętrzny `RerunException`,  
   - Dzięki temu kod działa na różnych wersjach Streamlita.

---

## Wymagania

- Python ≥ 3.7  
- streamlit ≥ 1.0 (testowane na 1.44.1)  

Instalacja zależności:

```bash
pip install streamlit
```

---

## Struktura Projektu

```
├── streamlit_app.py    # Główny skrypt aplikacji
└── users.json          # (generowany automatycznie) baza użytkowników
```

> Uwaga: Nie nazywaj swojego pliku `streamlit.py` ani nie twórz folderu `streamlit/` w projekcie – może to shadowować oryginalną bibliotekę.

---

## Uruchomienie

1. Otwórz terminal w katalogu z projektem.  
2. Uruchom:

   ```bash
   streamlit run streamlit_app.py
   ```

3. Przeglądarka automatycznie otworzy interfejs.

---

## Domyślne Konto Administratora

Przy pierwszym uruchomieniu, gdy `users.json` nie istnieje, aplikacja tworzy konto:

- login: **admin**  
- hasło: **admin**  
- rola: **admin**

**Zalecenie**: po pierwszym starcie zmień hasło admina lub usuń bootstrap i załaduj własnych użytkowników.

---

## Dostosowanie

- **Zastąp plik JSON** prawdziwą bazą (SQLite, PostgreSQL, LDAP itp.).  
- **Ulepsz hashowanie**: użyj bcrypt/scrypt z salt.  
- **Dodaj kolejne role** i strony.  
- **Zmień interfejs**: użyj kolumn, sekcji, layoutów Streamlita.  

---

## Bezpieczeństwo

- Przykład jest edukacyjny – w produkcji:
  - Nie używaj SHA-256 bez soli,  
  - Chroń bazę użytkowników,  
  - Użyj HTTPS,  
  - Zadbaj o CSRF/SQL-Injection jeśli łączysz z zewnętrzną bazą.
