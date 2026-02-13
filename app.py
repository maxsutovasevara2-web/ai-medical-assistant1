import streamlit as st
import openai
import os
import matplotlib.pyplot as plt

# --- Подключение ключа ---
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="ИИ-мед ассистент 🫁", page_icon="🫁")
st.title("ИИ-мед ассистент по симптомам пневмонии")
st.warning("⚠️ Это не диагноз! Точный диагноз может поставить только врач.")

# --- Инициализация состояния ---
if "risk_calculated" not in st.session_state:
    st.session_state.risk_calculated = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Ввод симптомов ---
user_text = st.text_input("Опишите свои симптомы:", placeholder="Например: кашель, слакбость, температура")

# --- Пошаговые вопросы ---
st.subheader("Пошаговые вопросы")
temp = st.radio("Температура выше 38°C?", ["Не знаю", "Да", "Нет"])
breath = st.radio("Есть ли одышка?", ["Не знаю", "Да", "Нет"])
chest = st.radio("Боль в груди при дыхании?", ["Не знаю", "Да", "Нет"])
weakness = st.radio("Сильная слабость?", ["Не знаю", "Да", "Нет"])

# --- Кнопка для оценки риска ---
if st.button("🤖 Оценить риск"):
    risk = 0
    explanation = []
    text = user_text.lower()

    # --- Анализ текста ---
    if "кашел" in text:
        risk += 1
        explanation.append("Кашель: возможная простуда или бронхит.")
    if "температур" in text:
        risk += 2
        explanation.append("Температура указывает на воспаление.")

    # --- Анализ ответов ---
    if temp == "Да":
        risk += 2
        explanation.append("Высокая температура усиливает риск инфекции.")
    if breath == "Да":
        risk += 3
        explanation.append("Одышка — важный признак возможного поражения лёгких.")
    if chest == "Да":
        risk += 3
        explanation.append("Боль в груди указывает на воспаление лёгких.")
    if weakness == "Да":
        risk += 1
        explanation.append("Слабость часто сопровождает серьёзные инфекции.")
    if "кашел" in text and chest == "Да":
        risk += 2
        explanation.append("Кашель + боль в груди повышают риск пневмонии.")

    probability = min(risk * 10, 95)

    # --- Визуализация ---
    st.subheader("🧠 Результат ИИ")
    categories = ['Риск', 'Остальное']
    values = [probability, 100 - probability]

    fig, ax = plt.subplots()
    ax.pie(values, labels=categories, colors=['red', 'green'], autopct='%1.0f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # --- Пояснения ---
    if probability < 30:
        st.success(f"Вероятность пневмонии низкая (~{probability}%).")
    elif probability < 60:
        st.warning(f"Вероятность пневмонии средняя (~{probability}%).")
    else:
        st.error(f"Вероятность пневмонии повышена (~{probability}%). Срочно обратитесь к врачу!")

    st.write("📌 Подробности анализа:")
    for e in explanation:
        st.write("–", e)

    st.session_state.risk_calculated = True  # сохраняем состояние

# --- Чат с ИИ ---
if st.session_state.risk_calculated:
    st.subheader("💬 Задайте любые вопросы ИИ")
    user_question = st.text_input("Ваш вопрос о симптомах:")

    if st.button("Ответ ИИ") and user_question:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты ИИ-медицинский ассистент. Дай понятный и безопасный ответ, без точного диагноза."},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.7,
                max_tokens=300
            )
            answer = response.choices[0].message.content
            # Сохраняем историю чата
            st.session_state.chat_history.append(("Пациент", user_question))
            st.session_state.chat_history.append(("ИИ", answer))
        except Exception as e:
            st.error(f"Ошибка при обращении к ИИ: {e}")

    # --- Отображаем историю чата ---
    for role, msg in st.session_state.chat_history:
        if role == "Пациент":
            st.info(f"🧑 {msg}")
        else:
            st.success(f"🤖 {msg}")
