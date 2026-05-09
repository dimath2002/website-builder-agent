# 🤖 Website Builder Agent

Αυτόματη δημιουργία websites για επιχειρήσεις στα **Χανιά** μέσω **Gemini AI** + **GitHub Pages**.

## Πώς λειτουργεί

1. Διαβάζει επιχειρήσεις από το `leads.json`
2. Καλεί το **Gemini AI** για να γράψει επαγγελματικό copy στα Ελληνικά
3. Δημιουργεί **3D animated HTML website** με Three.js
4. Ανεβάζει αυτόματα σε **GitHub Pages** (live URL σε ~60 δευτερόλεπτα)
5. Αποθηκεύει τα αποτελέσματα στο `results.md`

## Πότε τρέχει

- **Αυτόματα** κάθε μέρα στις 9:00 πρωί (UTC)
- **Αυτόματα** όταν αλλάξει το `leads.json`
- **Χειροκίνητα** από το GitHub Actions UI (workflow_dispatch)

## Secrets που χρειάζονται

| Secret | Πού το βρίσκεις |
|--------|-----------------|
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) |
| `GH_PAT` | GitHub → Settings → Developer Settings → Personal Access Tokens |
| `GH_USERNAME` | Το GitHub username σου |

## Προσθήκη νέας επιχείρησης

Απλά πρόσθεσε ένα νέο entry στο `leads.json` και κάνε push — το workflow τρέχει αυτόματα!

```json
{
  "business_name": "Το Όνομα",
  "business_type": "Τύπος Επιχείρησης",
  "description": "Σύντομη περιγραφή...",
  "phone": "28210 XXXXX",
  "email": "info@example.gr",
  "address": "Οδός Αριθμός, Χανιά",
  "city": "Χανιά",
  "hours": "Δευ-Παρ 9:00-17:00"
}
```

## Αποτελέσματα

Δες το [results.md](results.md) για όλα τα live URLs.
