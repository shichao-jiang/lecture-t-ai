import speech_recognition as sr
from os import path
from pydub import AudioSegment
import torch
import json 
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
import textwrap
from audiosplitter import split
from google.cloud import speech
from gcloud_transcribe import transcribe_file
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

#delete this aftewards (for converting vid to text)
import os
#from moviepy.editor import *
#video = VideoFileClip("cruise2m.mp4")
#video.audio.write_audiofile("transcribe_sound.mp3")
def transcribe(): 
    audio = AudioSegment.from_file("file.webm")
    audio.export("transcribe_sound.mp3", format="mp3")

    clipnum = split("transcribe_sound.mp3")
    print(clipnum)
    # convert mp3 file to wav                                                       

    transcription = ""
    i = 0
    while i < (clipnum+1):

        transcription += " " + transcribe_file("chunks/chunk" + str(i) + ".wav")
        i += 1

    print(transcription)

    lines = textwrap.wrap(transcription, 2000, break_long_words=False)

    z = 0

    lineslen = len(lines)

    model = T5ForConditionalGeneration.from_pretrained('t5-base')
    tokenizer = T5Tokenizer.from_pretrained('t5-base')
    device = torch.device('cpu')

    tokenizer2 = AutoTokenizer.from_pretrained("valhalla/t5-base-e2e-qg")
    model2 = AutoModelForSeq2SeqLM.from_pretrained("valhalla/t5-base-e2e-qg")

    questions = []

    while z < lineslen:
        text = lines[z]
        preprocess_text = text.strip().replace("\n","")
        t5_prepared_Text = "summarize: "+preprocess_text

        tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt").to(device)
        # summmarize 
        summary_ids = model.generate(tokenized_text,
                                            num_beams=4,
                                            no_repeat_ngram_size=2,
                                            min_length=70,
                                            max_length=100,
                                            early_stopping=True)

        output = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        print ("\n\nSummarized text number " + str((z+1)) +": \n",output)
        
        #Question Generation
        tokenized_text2 = tokenizer2.encode(output, return_tensors="pt").to(device)
        # summmarize 
        summary_ids2 = model2.generate(tokenized_text2,
                                            num_beams=4,
                                            max_decoding_length=64 ,)

        output2 = tokenizer2.decode(summary_ids2[0], skip_special_tokens=True)                                        

        print ("\n\nGenerated Question " + str((z+1)) +": \n",output2)
        asdf = output2.split("<sep>")
        for question in asdf:
            questions.append(question)
        z += 1
    return questions        
