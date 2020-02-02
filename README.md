# peller_quizzie
Сервис для прохождения опросов с вариантами ответов 

---
* Python 3.7 (Sanic)
* PostgreSQL

Запуск
---

```
docker-compose up --b
```


Тесты
---

Для запуска тестов в Dockerfile раскомментировать `# CMD ["pytest", "app/tests.py"]` и закомментировать`CMD ["python3", "run.py"]`
