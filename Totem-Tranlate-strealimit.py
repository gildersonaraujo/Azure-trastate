import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import time

# 🔑 Credenciais Azure Speech
speech_key = speech_key = "8HMuCkocwvN2FNG9lSFZEYdf6K41IngpW0Ghu5NQv8kDDEj7b4hhJQQJ99BGACZoyfiXJ3w3AAAYACOGbGA1"
service_region = "brazilsouth"

# 🔊 Dicionário de vozes
VOZES = {
    "pt": {
        "Feminina": "pt-BR-FranciscaNeural",
        "Masculina": "pt-BR-AntonioNeural"
    },
    "en": {
        "Feminina": "en-US-JennyNeural",
        "Masculina": "en-US-GuyNeural"
    }
}

# 🎙️ Criação do recognizer com auto-detecção
def criar_recognizer_auto():
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=speech_key,
        region=service_region
    )
    translation_config.add_target_language("en")
    translation_config.add_target_language("pt")

    auto_detect = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "pt-BR"]
    )
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config,
        audio_config=audio_config,
        auto_detect_source_language_config=auto_detect
    )
    return recognizer

# 🔊 Criar sintetizadores
def criar_sintetizadores(voz_pt, voz_en):
    config_pt = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    config_pt.speech_synthesis_voice_name = voz_pt
    sintetizador_pt = speechsdk.SpeechSynthesizer(speech_config=config_pt)

    config_en = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    config_en.speech_synthesis_voice_name = voz_en
    sintetizador_en = speechsdk.SpeechSynthesizer(speech_config=config_en)

    return sintetizador_en, sintetizador_pt

# 🧠 Tradução com auto-detecção
def traduzir(recognizer, sintetizador_en, sintetizador_pt):
    st.info("🎙️ Ouvindo... Fale agora.")
    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.TranslatedSpeech:
        idioma = result.properties[speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
        texto = result.text
        traducoes = result.translations

        st.success(f"🌐 Idioma detectado: `{idioma}`")
        st.markdown(f"**🗨️ Você disse:** {texto}")

        if idioma.startswith("en"):
            traducao = traducoes.get("pt")
            st.markdown(f"**🔁 Tradução (para PT):** {traducao}")
            sintetizador_pt.speak_text_async(traducao).get()

        elif idioma.startswith("pt"):
            traducao = traducoes.get("en")
            st.markdown(f"**🔁 Tradução (para EN):** {traducao}")
            sintetizador_en.speak_text_async(traducao).get()
        else:
            st.error("⚠️ Idioma não reconhecido ou não suportado.")

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancel = result.cancellation_details
        st.error(f"❌ Erro: {cancel.reason}")
        if cancel.reason == speechsdk.CancellationReason.Error:
            st.error(f"📄 Detalhes: {cancel.error_details}")

# ================= STREAMLIT =================

st.set_page_config(page_title="Totem Voz Azure", layout="centered")
st.title("🧠 Totem Tradutor Voz Azure")

st.sidebar.header("🎚️ Escolha as vozes")

voz_pt = st.sidebar.selectbox("🔊 Voz em Português", list(VOZES["pt"].keys()))
voz_en = st.sidebar.selectbox("🔊 Voz em Inglês", list(VOZES["en"].keys()))

# Carregar vozes completas
voz_pt_nome = VOZES["pt"][voz_pt]
voz_en_nome = VOZES["en"][voz_en]

# Botão principal
if st.button("🎤 Falar e Traduzir"):
    recognizer = criar_recognizer_auto()
    sintetizador_en, sintetizador_pt = criar_sintetizadores(voz_pt_nome, voz_en_nome)
    traduzir(recognizer, sintetizador_en, sintetizador_pt)
