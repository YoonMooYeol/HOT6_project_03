import os
import datetime
import speech_recognition as sr

class MicrophoneRecorder:
    def __init__(self, output_dir="recordings", file_format="wav"):
        """
        output_dir: 녹음 파일이 저장될 디렉토리.
        file_format: 저장할 파일 형식 (현재는 WAV 형식만 지원).
        """
        self.recognizer = sr.Recognizer()
        self.output_dir = output_dir
        self.file_format = file_format
        os.makedirs(self.output_dir, exist_ok=True)  # 저장 폴더 생성

    def record(self, duration=None):
        """
        마이크로부터 음성을 녹음합니다.
        duration: 녹음 시간(초, 옵션). 지정하지 않으면 자동 감지 후 기본 시간 기록.
        Returns:
          녹음된 audio 객체.
        """
        with sr.Microphone() as source:
            print("주변 소음 보정 중... 잠시만 기다려주세요.")
            self.recognizer.adjust_for_ambient_noise(source)
            print("녹음 시작! 말해보세요...")
            # phrase_time_limit: 지정한 초만큼 녹음. (None이면 수동 중단 필요하지만, 일반적으로 자동 중지되진 않음)
            audio = self.recognizer.listen(source, phrase_time_limit=duration)
        return audio

    def save_audio(self, audio, filename=None):
        """
        녹음된 음성을 파일로 저장합니다.
        
        audio: record() 메서드에서 반환된 audio 객체.
        filename: 저장할 파일명 (옵션). 지정하지 않으면 타임스템프 기반 이름 사용.
        
        Returns:
          저장된 파일의 경로.
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.{self.file_format}"
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "wb") as f:
            f.write(audio.get_wav_data())
        print(f"음성 파일이 저장되었습니다: {file_path}")
        return file_path

    def record_and_save(self, duration=None, filename=None):
        """
        음성을 녹음하고 자동으로 파일에 저장한 후, 파일 경로를 반환합니다.
        
        duration: 녹음 시간(초, 옵션).
        filename: 저장할 파일명 (옵션).
        
        Returns:
          저장된 파일의 전체 경로.
        """
        audio = self.record(duration=duration)
        return self.save_audio(audio, filename) 