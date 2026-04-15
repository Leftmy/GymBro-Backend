# Backend (Django + DRF)

## 🎯 Goal
Побудувати REST API для управління користувачами, тренуваннями, вправами та контентом.

---

# 🧑‍💻 User Stories

## 👤 Authentication & Users

### US-BE-1: Реєстрація користувача
**As a** new user  
**I want** to register  
**So that** I can use the system  

**Acceptance Criteria:**
- [ ] Можна зареєструватись через username/email/password
- [ ] Пароль хешується
- [ ] Унікальність email/username

---

### US-BE-2: Авторизація
- [ ] JWT authentication
- [ ] Refresh token
- [ ] Logout

---

## 💪 Exercises

### US-BE-3: Перегляд вправ
**As a user**  
**I want** to see exercises  
**So that** I can build workouts  

**Acceptance Criteria:**
- [ ] GET /exercises
- [ ] Фільтрація по:
  - difficulty
  - muscle group
  - equipment

---

### US-BE-4: Деталі вправи
- [ ] опис
- [ ] відео
- [ ] м'язи (primary/secondary)

---

## 🏋️ Workout Plans

### US-BE-5: Створення плану тренування
- [ ] POST /workout-plans
- [ ] Прив'язка до користувача

---

### US-BE-6: Додавання вправ у план
- [ ] sets
- [ ] reps
- [ ] rest
- [ ] order

---

### US-BE-7: Призначення плану користувачу
- [ ] лише 1 активний план
- [ ] деактивація попереднього

---

### US-BE-8: Отримання активного плану
- [ ] GET /me/active-plan

---

## 📊 Workout Sessions

### US-BE-9: Почати тренування
- [ ] створення WorkoutSession

---

### US-BE-10: Записати сет
- [ ] вага
- [ ] повторення

---

### US-BE-11: Завершити тренування
- [ ] фіксація часу

---

## 📝 Blog / Posts

### US-BE-12: Створення поста
- [ ] title
- [ ] body
- [ ] status (draft/published)

---

### US-BE-13: Коментарі
- [ ] CRUD comments

---

## 🔔 Notifications (інтеграція)

### US-BE-14: Тригер нагадування
- [ ] при активному плані
- [ ] відправка в notification service / celery

---

# 🧱 Technical Tasks

- [ ] DRF serializers
- [ ] ViewSets / APIViews
- [ ] Permissions
- [ ] Service layer
- [ ] Selectors
- [ ] Pagination
- [ ] Filtering (django-filter)
- [ ] Testing (pytest)
