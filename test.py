from gradio_client import Client, handle_file

client = Client("eustlb/whisper-vs-distil-whisper-fr")
result = client.predict(
		inputs=handle_file('records/téléchargement.wav'),
		api_name="/transcribe"
)
print(result[0])
