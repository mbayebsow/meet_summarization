from openai import OpenAI
import sounddevice as sd
from scipy.io.wavfile import write
import customtkinter
# import speech_recognition as sr
# from transformers import pipeline
from datetime import datetime
import numpy as np
from gradio_client import Client, handle_file
import threading
import time
import sqlite3
# from PIL import Image, ImageTk
import pygame
from tkinter import ttk
import markdown2
from tkhtmlview import HTMLLabel
from plyer import notification
import os


# $0.35/$0.40 in/out Mtoken - meta-llama/Meta-Llama-3.1-70B-Instruct
# $0.06 / Mtoken - google/gemma-2-9b-it
TRANS = "bonjour à tous merci de vous joindre à cette réunion aujourd'hui nous allons discuter du processus d'intégration de la nouvelle fonctionnalité de notification en temps réel dans notre application je voudrais que nous passions en revue chaque étape pour nous assurer que tout est clair Sophie tu pourrais commencer par expliquer l'architecture que tu as proposé bien sûr Sarah poney pour cette fonctionnalité j'ai pensé à utiliser une architecture basée sur des web socket cela nous permettrait de maintenir une connexion ouverte entre le client et le serveur garantissant que les notifications sont reçus en temps réel sans avoir besoin de recharger la page nous pourrions également implémenter une file d'attente pour gérer les messages en cas de déconnexion temporaire merci Sophie Mathieu en tant que responsable du bacon penses-tu que cette approche est réalisable avec notre infrastructure actuelle oui je pense que c'est une bonne solution notre serveur est déjà capable de gérer des connexions WebSocket mais nous devrons nous assurer que les messages sont bien envoyés en utilisant un système de publication abonnement point point cela nous permettra de diffuser les notifications uniquement aux utilisateurs concernés ce qui minimiser la charge sur le serveur d'accord Kévin comment penses-tu que cela affectera l'interface utilisateur l'intégration des notifications en temps réel dans l'interface utilisateur nécessitera quelques ajustements par exemple nous devrons ajouter un indicateur visuel pour notifier l'utilisateur d'un nouveau message point point je suggère également d'ajouter une option permettant de désactiver les notifications en temps réel pour ceux qui préfèrent ne pas être dérangé tu es une bonne idée je pourrais ajouter un paramètre dans le bac and pour gérer les préférences de l'utilisateur en matière de notification point point pour ce qui est du back-end il faudra aussi vérifier la sécurité de la connexion WebSocket pantin nous devons nous assurer que seuls les utilisateurs authentifiés peuvent recevoir des notifications je vais configurer un token d'authentification pour chaque session WebSocket excellent je pense que nous sommes sur la bonne voie une fois que la fonctionnalité est développée quel est le plan pour les tests Kévin nous devons effectuer des tests unitaires pour chaque composant de l'interface utilisateur ainsi que des tests d'intégration pour vérifier que les notifications fonctionnent correctement dans différents scénarios je pense aussi que des tests de charge seront nécessaires pour voir comment notre système gère un grand nombre de notifications en même temps je suis d'accord il serait aussi prudent d'effectuer un test en condition réelle avec un groupe d'utilisateurs beta avant de lancer la fonctionnalité à grande échelle putois parfait je propose que nous préparions à un plan de test détaillé pour nous assurer que rien n'est laissé au hasard est-ce que quelqu'un a d'autres commentaires ou suggestions rien de plus de mon côté tout semble bien couvert je vais commencer à travailler sur les maquettes pour l'interface utilisateur je vous les enverrai pour révision d'ici la fin de la semaine je vais m'occuper de la mise en place du back-end dès que possible très bien merci à tous pour votre participation nous avons un plan clair maintenant je vous enverrai un récapitulatif avec les prochaines étapes après cette réunion bonne journée à tous"
MODEL_NAME = "google/gemma-2-9b-it"
BASE_URL = "https://api.deepinfra.com/v1/openai"
DEEPINFRA_API_KEY = "H5S6vrdfPCeygxuD0joSKAuYcLWFq0CG"
DEEPGRAM_API_KEY = "YOUR_SECRET"
RECORDINGS_DB = 'recordings.db'
IS_RECORDING = False
FS = 44100
RECORDING = []
FILENAME = ""
START_TIME = None
IS_PLAYING = False
OPENAI = OpenAI(
    api_key=DEEPINFRA_API_KEY,
    base_url=BASE_URL,
)
client = Client("eustlb/whisper-vs-distil-whisper-fr")

def get_input_devices():
    devices = sd.query_devices()
    input_devices = {device['name']: index for index, device in enumerate(devices) if device['max_input_channels'] > 0}
    return input_devices

def audio_callback(indata, frames, time, status):
    if IS_RECORDING:
        RECORDING.append(indata.copy())

def toggle_recording_indicator():
    while IS_RECORDING:
        recording_indicator.config(fg_color="red" if recording_indicator.cget("fg_color") == "black" else "black")
        root.update()
        time.sleep(0.5)
    recording_indicator.config(fg_color="black")

def start_recording():
    global input_device_var, input_devices, IS_RECORDING, START_TIME, RECORDING
    IS_RECORDING = True
    START_TIME = datetime.now()
    RECORDING = []
    print("Recording...")
    selected_device_name = input_device_var.get()
    selected_device_index = input_devices[selected_device_name]
    stream = sd.InputStream(samplerate=FS, channels=1, device=selected_device_index, callback=audio_callback)
    stream.start()
    threading.Thread(target=toggle_recording_indicator).start()
    
    # Notification de début d'enregistrement
    notification.notify(
        title="Enregistrement",
        message="L'enregistrement a commencé.",
        timeout=5
    )
    
    return stream

def stop_recording(stream):
    global IS_RECORDING, FILENAME, START_TIME, TRANS
    if IS_RECORDING:
        IS_RECORDING = False
        stream.stop()
        stream.close()
        end_time = datetime.now()
        duration = (end_time - START_TIME).seconds
        FILENAME = f"meet_{START_TIME.strftime('%Y%m%d_%H%M%S')}_{duration}s.wav"
        recording_np = np.concatenate(RECORDING, axis=0)
        write(FILENAME, FS, recording_np)
        print(f"Recording saved as {FILENAME}")
        
        # Notification de fin d'enregistrement
        notification.notify(
            title="Enregistrement",
            message=f"L'enregistrement est terminé. Fichier sauvegardé sous {FILENAME}.",
            timeout=5
        )
        
        root.update()
        # transcription = transcribe_audio(FILENAME)
        
        # # Notification de transcription réussie
        # notification.notify(
        #     title="Transcription",
        #     message="La transcription est terminée.",
        #     timeout=5
        # )
        
        root.update()
        # summary = summarize_text(TRANS)
        
        # # Notification de résumé terminé
        # notification.notify(
        #     title="Résumé",
        #     message="Le résumé est terminé.",
        #     timeout=5
        # )
        
        # save_recording_to_db(FILENAME, transcription, summary)
        # text_output.insert(tk.END, f"Transcription:\n{TRANS}\n\nRésumé:\n{summary}\n")
        update_recording_list()

def transcribe_audio(FILENAME):
    # recognizer = sr.Recognizer()
    # with sr.AudioFile("records/téléchargement.wav") as source:
    #     audio = recognizer.record(source)
    try:
        # text = recognizer.recognize_google(audio, language="fr-FR")
        result = client.predict(
            inputs=handle_file('records/records/téléchargement.wav'),
            api_name="/transcribe"
        )
        print("Transcription réussie.")
        return result[0]
    # except sr.UnknownValueError:
    #     print("La reconnaissance vocale n'a pas compris l'audio.")
    except Exception as e:
        print("Erreur lors de la demande de reconnaissance vocale.")
    return ""

def summarize_text(text):
    global MODEL_NAME, OPENAI
    response = OPENAI.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": f"Fait moi un résumé de ce texte en y ajouter un titre, des points clès, des points important souligner : {text}"}],
    )
    summary = response.choices[0].message.content
    # print(response.usage.prompt_tokens, response.usage.completion_tokens)
    return summary

def start_recording_button():
    global stream
    stream = start_recording()
    start_r_button.pack_forget()
    stop_r_button.pack()

def stop_recording_button():
    stop_recording(stream)
    stop_r_button.pack_forget()
    start_r_button.pack()

def init_db():
    conn = sqlite3.connect(RECORDINGS_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recordings
                 (id INTEGER PRIMARY KEY, filename TEXT, transcription TEXT, summary TEXT)''')
    conn.commit()
    conn.close()

def save_recording_to_db(filename, transcription, summary):
    conn = sqlite3.connect(RECORDINGS_DB)
    c = conn.cursor()
    c.execute("INSERT INTO recordings (filename, transcription, summary) VALUES (?, ?, ?)",
              (filename, transcription, summary))
    conn.commit()
    conn.close()

def load_recordings():
    conn = sqlite3.connect(RECORDINGS_DB)
    c = conn.cursor()
    c.execute("SELECT id, filename FROM recordings")
    recordings = c.fetchall()
    conn.close()
    return recordings

def format_filename(filename):
    # Extrait la date et l'heure du nom du fichier
    parts = filename.split('_')
    date_part = parts[1]
    time_part = parts[2].split('s')[0]
    date = datetime.strptime(date_part + time_part, '%Y%m%d%H%M%S')
    formatted_date = date.strftime('%d/%m/%Y à %Hh%M')
    return f"Meet du {formatted_date}"

def update_recording_list():
    recordings = load_recordings()
    recording_listbox.delete(0, ctk.END)
    for recording in recordings:
        formatted_name = format_filename(recording[1])
        recording_listbox.insert(ctk.END, formatted_name)

def on_recording_select(event):
    if not recording_listbox.curselection():
        return
    selected_formatted_name = recording_listbox.get(recording_listbox.curselection())
    # Trouver le nom de fichier original correspondant au nom formaté
    recordings = load_recordings()
    for recording in recordings:
        if format_filename(recording[1]) == selected_formatted_name:
            recording_id = recording[0]
            break
    display_recording_details(recording_id)

def save_transcription():
    print("before_save_transcription")
    if not recording_listbox.curselection():
        return
    print("save_transcription")
    selected_formatted_name = recording_listbox.get(recording_listbox.curselection())
    recordings = load_recordings()
    for recording in recordings:
        if format_filename(recording[1]) == selected_formatted_name:
            recording_id = recording[0]
            break
    new_transcription = transcription_text.get(1.0, ctk.END).strip()
    update_transcription_in_db(recording_id, new_transcription)
    
    # Notification de transcription enregistrée
    notification.notify(
        title="Transcription",
        message="La transcription a été enregistrée avec succès.",
        timeout=5
    )
    
    root.update()
    new_summary = summarize_text(new_transcription)
    update_summary_in_db(recording_id, new_summary)
    
    # Notification de résumé mis à jour
    notification.notify(
        title="Résumé",
        message="Le résumé a été mis à jour avec succès.",
        timeout=5
    )
    
    display_recording_details(recording_id)

def update_transcription_in_db(recording_id, new_transcription):
    conn = sqlite3.connect(RECORDINGS_DB)
    c = conn.cursor()
    c.execute("UPDATE recordings SET transcription = ? WHERE id = ?", (new_transcription, recording_id))
    conn.commit()
    conn.close()

def update_summary_in_db(recording_id, new_summary):
    conn = sqlite3.connect(RECORDINGS_DB)
    c = conn.cursor()
    c.execute("UPDATE recordings SET summary = ? WHERE id = ?", (new_summary, recording_id))
    conn.commit()
    conn.close()

def display_recording_details(recording_id):
    conn = sqlite3.connect(RECORDINGS_DB)
    c = conn.cursor()
    c.execute("SELECT filename, transcription, summary FROM recordings WHERE id=?", (recording_id,))
    recording = c.fetchone()
    conn.close()
    if recording:
        filename, transcription, summary = recording
        if IS_PLAYING:
            stop_audio() 
        # play_button.config(command=lambda: play_audio(filename))
        # stop_button.config(command=stop_audio)
        transcription_text.delete(1.0, ctk.END)
        transcription_text.insert(ctk.END, transcription)
        summary_html = markdown2.markdown(summary)
        summary_label.set_html(summary_html)

def start_or_resume_audio():
    global IS_PLAYING
    if not IS_PLAYING:
        play_audio(FILENAME)
        play_button.pack_forget()
        pause_button.pack()
        IS_PLAYING = True
    else:
        resume_audio()

def play_audio(filename):
    global is_paused
    pygame.mixer.init()
    pygame.mixer.music.load("records/téléchargement.wav")
    pygame.mixer.music.play()
    play_button.pack_forget()
    pause_button.pack()
    is_paused = False
    update_progress_bar()

def pause_audio():
    global is_paused
    if not is_paused:
        pygame.mixer.music.pause()
        play_button.pack()
        pause_button.pack_forget()
        is_paused = True

def resume_audio():
    global is_paused
    if is_paused:
        pygame.mixer.music.unpause()
        play_button.pack_forget()
        pause_button.pack()
        is_paused = False
        update_progress_bar()

def stop_audio():
    global IS_PLAYING
    pygame.mixer.music.stop()
    play_button.pack()
    pause_button.pack_forget()
    IS_PLAYING = False
    update_progress_bar()

def update_progress_bar():
    if pygame.mixer.music.get_busy():
        current_time = pygame.mixer.music.get_pos() / 1000  # Convertir en secondes
        duration = get_audio_duration(FILENAME)  # Obtenir la durée de l'audio
        progress = (current_time / duration) * 100
        progress_bar['value'] = progress
        duration_label.config(text=f"Durée: {current_time:.2f}s / {duration:.2f}s")
        root.after(1000, update_progress_bar)

def get_audio_duration(filename):
    return os.path.getsize("records/téléchargement.wav") / (FS * 2)  # Estimation de la durée

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{900}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.content_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0,fg_color="transparent")
        self.content_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="CustomTkinter", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.input_devices = get_input_devices()
        self.input_device_var = customtkinter.StringVar()
        self.input_device_var.set(list(self.input_devices.keys())[0])  # Définir le premier périphérique comme valeur par défaut
        self.input_device_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, width=150,dynamic_resizing=False,variable=self.input_device_var, values=list(self.input_devices.keys()))
        self.input_device_optionemenu.grid(row=1, column=0, padx=5, pady=10)

        self.start_recording_button = customtkinter.CTkButton(self.sidebar_frame, text="Démarrer l'enregistrement", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=start_recording)
        self.start_recording_button.grid(row=2, column=0, padx=5, pady=10)


        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # create slider and progressbar frame
        self.slider_progressbar_frame = customtkinter.CTkFrame(self.content_frame,)
        self.slider_progressbar_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(0, weight=1)
        self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_2.grid(row=0, column=0, sticky="ew")

        # create tabview
        self.tabview = customtkinter.CTkTabview(self.content_frame, width=250, height=250)
        self.tabview.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tabview.add("Transcription")
        self.tabview.add("Resumer")
        self.tabview.tab("Transcription").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Transcription").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Resumer").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Resumer").grid_rowconfigure(0, weight=1)

        self.textbox = customtkinter.CTkTextbox(self.tabview.tab("Transcription"), width=250, height=250)
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.save_transcription_button = customtkinter.CTkButton(self.tabview.tab("Transcription"), text="Enregistrer les modifications",)
        self.save_transcription_button.grid(row=1, column=0, padx=10, pady=5, sticky="se")

        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Resumer"), text="CTkLabel on Tab 2")
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.progressbar_2.set(1)
        self.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)


    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

app = App()
app.mainloop()
