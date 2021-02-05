from pydub import AudioSegment
#from pydub.utils import mediainfo
from pydub.utils import make_chunks
import math

def split(audiofile):
    given_audio = AudioSegment.from_file(audiofile, "mp3")
    given_audio = given_audio.set_channels(1)
    given_audio.export("audio.wav", format="wav")
    myaudio = AudioSegment.from_file("audio.wav" , "wav")
    channel_count = myaudio.channels    #Get channels
    sample_width = myaudio.sample_width #Get sample width
    duration_in_sec = len(myaudio) / 1000#Length of audio in sec
    sample_rate = myaudio.frame_rate

    print("sample_width=", sample_width )
    print("channel_count=", channel_count)
    print("duration_in_sec=", duration_in_sec )
    print("frame_rate=", sample_rate)
    bit_rate =16  #assumption , you can extract from mediainfo("test.wav") dynamically


    wav_file_size = (sample_rate * bit_rate * channel_count * duration_in_sec) / 8
    print("wav_file_size = ",wav_file_size)


    file_split_size = 10000000  # 10Mb OR 10, 000, 000 bytes
    total_chunks =  wav_file_size // file_split_size

    #Get chunk size by following method #There are more than one ofcourse
    #for  duration_in_sec (X) -->  wav_file_size (Y)
    #So   whats duration in sec  (K) --> for file size of 10Mb
    #  K = X * 10Mb / Y

    chunk_length_in_sec = math.ceil((duration_in_sec * 10000000 ) /wav_file_size)   #in sec
    chunk_length_ms = chunk_length_in_sec * 500
    chunks = make_chunks(myaudio, chunk_length_ms)

    #Export all of the individual chunks as wav filesc

    for i, chunk in enumerate(chunks):
        chunk_name = "chunk{0}.wav".format(i)
        print("exporting", chunk_name)
        chunk.export("chunks/"+chunk_name, format="wav")

    return i