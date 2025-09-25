import os
import base64
import tempfile
from typing import Any, Optional
from crewai.tools import BaseTool   # Base class for custom tools
# import openai                     # Audio processing: OpenAI Whisper API (disabled temporarily)
import whisper                      # Audio processing: Local whisper for transcription
from pathlib import Path            # File system: Path manipulation

# Tools can either be created with the @tool decorator or with the BaseTool library
# Here we are using BaseTool


#####################################################################
class AudioTranscriptionTool(BaseTool):
    """ Transcribes audio files into text """
    name: str = "Audio Transcription Tool"
    description: str = "Transcribes audio files (mp3, wav, m4a, etc.) into text for threat analysis. Input should be the path to an audio file."
    
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.whisper_model: Optional[Any] = None
    whisper_model: Optional[Any] = None
    
    def _load_whisper_model(self):
        """Load Whisper model lazily"""
        if self.whisper_model is None:
            # Use 'base' model for good balance of speed/accuracy
            # Options: tiny, base, small, medium, large
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model
    
    def _run(self, audio_path: str) -> str:
        try:
            # Verify file exists
            if not os.path.exists(audio_path):
                return f"Error: Audio file not found at {audio_path}"
            
            # Load and transcribe
            model = self._load_whisper_model()
            result = model.transcribe(audio_path)
            
            # Format output for threat analysis
            transcription = result['text']
            confidence = result.get('language_probability', 0.0)
            detected_language = result.get('language', 'unknown')
            
            formatted_output = f"""
            AUDIO TRANSCRIPTION REPORT:
            ==========================
            Detected Language: {detected_language} (confidence: {confidence:.2f})
            Transcription: {transcription}
            ==========================
            """
            return formatted_output.strip()
            
        except Exception as e:
            return f"Error processing audio file: {str(e)}"


#####################################################################
class DocumentAnalysisTool(BaseTool):
    name: str = "Document Analysis Tool"
    description: str = "Analyzes text documents, PDFs, and other written reports for threat intelligence. Input should be the path to a document file."
    
    def _run(self, document_path: str) -> str:
        try:
            # Verify file exists
            if not os.path.exists(document_path):
                return f"Error: Document file not found at {document_path}"
            
            file_extension = Path(document_path).suffix.lower()
            
            if file_extension == '.txt':
                content = self._read_text_file(document_path)
            elif file_extension == '.pdf':
                content = self._read_pdf_file(document_path)
            else:
                return f"Unsupported document type: {file_extension}"
            
  
            
            formatted_output = f"""
            DOCUMENT ANALYSIS REPORT:
            ========================
            File: {os.path.basename(document_path)}

            Content:
            {content}
            ========================
            """
            return formatted_output.strip()
            
        except Exception as e:
            return f"Error processing document: {str(e)}"
    
    def _read_text_file(self, file_path: str) -> str:
        """Read plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error reading text file: {str(e)}"
    
    def _read_pdf_file(self, file_path: str) -> str:
        """Read PDF file using PyPDF2"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except ImportError:
            return "PDF processing requires PyPDF2: pip install PyPDF2"
        except Exception as e:
            return f"Error reading PDF file: {str(e)}"

#####################################################################
class InputTypeDeterminerTool(BaseTool):
    name: str = "Input Type Determiner"
    description: str = "Determines the type of input (text, audio, image, document) and recommends which processing tool to use. Input should be either a file path or direct text content."
    
    def _run(self, input_data: str) -> str:
        # Check if it's a file path
        if os.path.exists(input_data):
            file_path = input_data
            file_extension = Path(file_path).suffix.lower()
            
            # Audio formats (temporarily disabled)
            if file_extension in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
                return f"""
                INPUT TYPE: AUDIO FILE
                Detected: {file_extension.upper()} audio file
                Recommendation: Use Audio Transcription Tool to convert to text
                File: {os.path.basename(file_path)}
                """
        
            # Document formats
            elif file_extension in ['.txt', '.pdf', '.doc', '.docx']:
                return f"""
                INPUT TYPE: DOCUMENT FILE
                Detected: {file_extension.upper()} document file
                Recommendation: Use Document Analysis Tool to process text content
                File: {os.path.basename(file_path)}
                """
            
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
                return f"""
                INPUT TYPE: IMAGE FILE
                Detected: {file_extension.upper()} image file
                Recommendation: Process this image yourself or use AddImageTool if available.
                Remember to look for visual threats in military context.
                File: {os.path.basename(file_path)}
                """
            
            
            else:
                return f"""
                INPUT TYPE: UNKNOWN FILE
                Detected: {file_extension.upper()} file (unsupported format)
                Recommendation: Convert to supported format, provide text directly or directly analyze
                File: {os.path.basename(file_path)}
                """
        
        # Assume it's direct text input
        else:
            word_count = len(input_data.split())
            return f"""
            INPUT TYPE: DIRECT TEXT
            Detected: Text input with {word_count} words
            Recommendation: Process directly for threat analysis
            No additional tools needed - ready for tactical assessment
            """